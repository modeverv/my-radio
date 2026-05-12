import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

_PLAYLIST_URL = "https://music.youtube.com/playlist?list=RDATd7X"
_ITEM_CSS     = "ytmusic-responsive-list-item-renderer"
_PLAY_BTN_CSS = "ytmusic-play-button-renderer"


class YTMPlayer:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)

        project_dir   = os.path.dirname(os.path.abspath(__file__))
        user_data_dir = os.path.join(project_dir, "chrome_profile")
        os.makedirs(user_data_dir, exist_ok=True)

        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-allow-origins=*")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        self._songs_played = 0  # 今のサイクルで再生した曲数

        try:
            print(f"[ytm_player] Chromeを起動中... (Profile: {user_data_dir})")
            self.service = Service(ChromeDriverManager().install())
            self.driver  = webdriver.Chrome(service=self.service, options=chrome_options)
            self.driver.set_window_size(1280, 1000)
            self.driver.get("https://music.youtube.com/")
            print("[ytm_player] YouTube Music を表示しました。")
        except Exception as e:
            print(f"\n--- CHROME STARTUP ERROR ---\n{e}")
            raise

    # ------------------------------------------------------------------
    # 公開API（main.py から呼ばれるメソッド）
    # ------------------------------------------------------------------

    def start(self):
        try:
            self.driver.get("https://music.youtube.com/")
        except Exception as e:
            print(f"[ytm_player] ホーム移動エラー: {e}")

    def start_random_playlist(self):
        """指定プレイリストを開き、逆順（末尾→先頭）で最初の曲を再生する"""
        try:
            print(f"[ytm_player] プレイリストを読み込み中...")
            self.driver.get(_PLAYLIST_URL)
            time.sleep(4)

            # スクロールして全曲をロード
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            items = self.driver.find_elements(By.CSS_SELECTOR, _ITEM_CSS)
            total = len(items)
            if not total:
                print("[ytm_player] 曲リストが見つかりませんでした。")
                return

            self._songs_played = 0
            print(f"[ytm_player] {total}曲を検出。末尾から逆順で再生します。")
            self._click_reverse(items)

        except Exception as e:
            print(f"[ytm_player] プレイリスト開始エラー: {e}")

    def next_track(self):
        """逆順で次の曲（1つ前の位置）へ"""
        items = self.driver.find_elements(By.CSS_SELECTOR, _ITEM_CSS)
        if not items:
            print("[ytm_player] 曲リストが取得できず。プレイリストを再読み込みします。")
            self.start_random_playlist()
            return
        self._click_reverse(items)

    def get_current_track_info(self) -> dict:
        try:
            wait      = WebDriverWait(self.driver, 5)
            title_el  = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytmusic-player-bar .title")))
            byline_el = self.driver.find_element(By.CSS_SELECTOR, "ytmusic-player-bar .byline")
            title     = title_el.text.strip()
            byline    = byline_el.text.strip()
            artist    = byline.split('•')[0].split('/')[0].strip() or "Unknown Artist"
            return {"title": title, "artist": artist}
        except Exception as e:
            print(f"[ytm_player] 曲情報取得失敗: {e}")
            return {"title": "不明な曲", "artist": "不明なアーティスト"}

    def fade_volume(self, target_volume: float, duration: float = 2.0):
        """JS でなめらかに音量を変化させる。フェードイン時は muted 解除と play() も補完"""
        try:
            script = f"""
            var target = {target_volume};
            var dur    = {duration * 1000};
            var video  = document.querySelector('video');
            if (!video) return;

            // フェードイン時: ミュート解除 & 停止していれば再生
            if (target > 0) {{
                video.muted = false;
                if (video.paused) {{ video.play().catch(function(){{}}); }}
            }}

            var startVol  = video.volume;
            var startTime = performance.now();

            var fade = setInterval(function() {{
                var progress = (performance.now() - startTime) / dur;
                if (progress >= 1) {{
                    video.volume = target;
                    clearInterval(fade);
                }} else {{
                    video.volume = startVol + (target - startVol) * progress;
                }}
            }}, 50);
            """
            self.driver.execute_script(script)
            time.sleep(duration)
        except Exception as e:
            print(f"[ytm_player] フェード実行エラー: {e}")

    def stop(self):
        """音量を0にして一時停止する"""
        try:
            self.driver.execute_script("""
                var v = document.querySelector('video');
                if (v) {
                    v.volume = 0.0;
                    v.muted   = true;
                    if (!v.paused) v.pause();
                }
            """)
            try:
                btn  = self.driver.find_element(By.ID, "play-pause-button")
                text = (btn.get_attribute("aria-label") or "") + (btn.get_attribute("title") or "")
                if any(k in text for k in ["Pause", "一時停止", "停止"]):
                    paused = self.driver.execute_script(
                        "var v = document.querySelector('video'); return v ? v.paused : true")
                    if not paused:
                        btn.click()
            except Exception:
                pass
            self.driver.execute_script(
                "try { var v=document.querySelector('video'); v.volume=0; v.muted=true; } catch(e) {}")
        except Exception as e:
            print(f"[ytm_player] 停止処理エラー: {e}")

    def quit(self):
        self.driver.quit()

    # ------------------------------------------------------------------
    # 内部ヘルパー
    # ------------------------------------------------------------------

    def _click_reverse(self, items: list):
        """items の末尾から _songs_played 番目の曲をクリックして再生する"""
        total  = len(items)
        target = total - 1 - self._songs_played

        if target < 0:
            print("[ytm_player] 全曲再生完了。プレイリストを最初からやり直します。")
            self.start_random_playlist()
            return

        item = items[target]
        try:
            # クリック前に消音
            self.driver.execute_script("""
                try { var v=document.querySelector('video'); if(v){ v.volume=0; v.muted=true; } } catch(e) {}
            """)

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
            time.sleep(0.5)

            # 再生ボタンを探してクリック、なければ行自体をクリック
            try:
                btn = item.find_element(By.CSS_SELECTOR, _PLAY_BTN_CSS)
                self.driver.execute_script("arguments[0].click();", btn)
            except Exception:
                self.driver.execute_script("arguments[0].click();", item)

            # クリック直後 2 秒間 volume=0, muted=false を維持（YTM が音量をリセットするのを防ぐ）
            self.driver.execute_script("""
                var iv = setInterval(function() {
                    var v = document.querySelector('video');
                    if (v) { v.volume = 0.0; v.muted = false; }
                }, 50);
                setTimeout(function() { clearInterval(iv); }, 2000);
            """)

            self._songs_played += 1
            print(f"[ytm_player] 逆順 {self._songs_played}/{total} (index={target}) を再生開始")

        except Exception as e:
            print(f"[ytm_player] クリックエラー (index={target}): {e}")
            self._songs_played += 1  # エラーでもスキップして次へ
