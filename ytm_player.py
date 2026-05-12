import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class YTMPlayer:
    def __init__(self):
        chrome_options = Options()
        # プロセス終了後もブラウザを残す
        chrome_options.add_experimental_option("detach", True)
        
        # プロジェクト内に専用のプロファイルディレクトリを作成
        project_dir = os.path.dirname(os.path.abspath(__file__))
        user_data_dir = os.path.join(project_dir, "chrome_profile")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
            
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        
        # 安定性のためのフラグ
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-allow-origins=*")
        
        # 自動操作の検知を回避
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        try:
            print(f"[ytm_player] Chromeを起動中... (Profile: {user_data_dir})")
            driver_path = ChromeDriverManager().install()
            self.service = Service(driver_path)
            self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
            self.driver.set_window_size(1280, 1000)
            
            # ユーザー様提供の最新チャートページを開く
            self.chart_url = "https://music.youtube.com/playlist?list=OLAK5uy_nMa6r07BbcC_Q8PrrS1CVHH2aGJRIkWu0"
            self.driver.get(self.chart_url)
            print("[ytm_player] YouTube Music 日本チャートを表示しました。")
        except Exception as e:
            print(f"\n--- CHROME STARTUP ERROR ---\n{e}")
            raise e

    def fade_volume(self, target_volume: float, duration: float = 2.0):
        """ブラウザ側(JS)で滑らかに音量を変化させる (1回の呼出しで完結)"""
        try:
            script = f"""
            var target = {target_volume};
            var duration = {duration * 1000};
            var video = document.querySelector('video');
            if (!video) {{
                console.log("fade_volume: video要素が見つかりません");
                return;
            }}
            
            var startVolume = video.volume;
            var startTime = performance.now();
            console.log("フェード開始: 現在の音量=" + startVolume + " -> 目標=" + target + " (" + duration + "ms)");
            
            var fade = setInterval(function() {{
                var elapsed = performance.now() - startTime;
                var progress = elapsed / duration;
                
                if (progress >= 1) {{
                    video.volume = target;
                    clearInterval(fade);
                    console.log("フェード完了: 現在の音量=" + video.volume);
                }} else {{
                    video.volume = startVolume + (target - startVolume) * progress;
                    // ログが多すぎないように10回に1回程度出力
                    if (Math.random() < 0.1) {{
                        console.log("フェード中... 現在の音量:", video.volume.toFixed(2));
                    }}
                }}
            }}, 50);
            """
            self.driver.execute_script(script)
            time.sleep(duration)
        except Exception as e:
            print(f"[ytm_player] フェード実行エラー: {e}")

    def start(self):
        try:
            print("[ytm_player] ホーム画面へ移動中...")
            self.driver.get("https://music.youtube.com/")
        except Exception as e:
            print(f"[ytm_player] 初期ページ: {e}")


    def start_random_playlist(self):
        """ホーム画面からランダムなプレイリストを選択して再生を開始する"""
        try:
            # 再生ボタン（オーバーレイ）を持つアイテムを探す
            # ytmusic-two-row-item-renderer はプレイリストやアルバムの一般的な要素
            selectors = [
                "ytmusic-two-row-item-renderer ytmusic-play-button-renderer",
                "ytmusic-responsive-list-item-renderer ytmusic-play-button-renderer",
                ".play-button"
            ]
            
            buttons = []
            for selector in selectors:
                found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if found:
                    buttons.extend(found)
            
            if not buttons:
                print("[ytm_player] 再生ボタンが見つかりませんでした。デフォルトのプレイリストを開きます。")
                self.driver.get("https://music.youtube.com/playlist?list=OLAK5uy_nMa6r07BbcC_Q8PrrS1CVHH2aGJRIkWu0")
                time.sleep(3)
                self.driver.find_element(By.CSS_SELECTOR, "ytmusic-play-button-renderer").click()
                return

            # クリック前に可能な限り音量を絞る準備（video要素が既に存在する場合）
            self.driver.execute_script("""
                try {
                    var v = document.querySelector('video');
                    if (v) { v.volume = 0.0; v.muted = true; }
                } catch(e) {}
            """)

            import random
            target = random.choice(buttons)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
            time.sleep(1)

            # クリック実行
            self.driver.execute_script("arguments[0].click();", target)
            print("[ytm_player] ランダムなプレイリストを選択しました。")

            # クリック直後、最速で音量を0にし、一時停止を試みる
            # (sleep 2秒を待たずに実行)
            self.driver.execute_script("""
                var interval = setInterval(function() {
                    var v = document.querySelector('video');
                    if (v) {
                        v.volume = 0.0;
                        v.muted = true;
                        v.pause();
                        // 状態が安定するまで数回繰り返す
                        if (v.paused && v.volume === 0) {
                            clearInterval(interval);
                        }
                    }
                }, 100);
                // 3秒経ったらあきらめる
                setTimeout(function() { clearInterval(interval); }, 3000);
            """)
        except Exception as e:
            print(f"[ytm_player] ランダム再生開始エラー: {e}")

    def get_current_track_info(self) -> dict:
        """現在再生中（または停止中）の曲名とアーティスト名を取得する"""
        try:
            # ロード待ちを考慮
            wait = WebDriverWait(self.driver, 5)
            title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytmusic-player-bar .title")))
            byline_elem = self.driver.find_element(By.CSS_SELECTOR, "ytmusic-player-bar .byline")
            
            title = title_elem.text.strip()
            byline = byline_elem.text.strip()
            
            # bylineからアーティスト名のみを抽出
            artist = byline.split('•')[0].split('/')[0].strip()
            if not artist:
                artist = "Unknown Artist"
            
            return {"title": title, "artist": artist}
        except Exception as e:
            print(f"[ytm_player] 曲情報取得失敗: {e}")
            return {"title": "不明な曲", "artist": "不明なアーティスト"}

    def next_track(self):
        """次の曲へスキップする"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, ".next-button")
            next_button.click()
            print("[ytm_player] 次の曲へスキップしました。")
        except Exception as e:
            print(f"[ytm_player] スキップ失敗: {e}")
    def stop(self):
        """再生を停止し、音量を完全に0にする"""
        try:
            # 1. JSで音量を0にし、一時停止（ミュートもかける）
            self.driver.execute_script("""
                var video = document.querySelector('video');
                if (video) {
                    video.volume = 0.0;
                    video.muted = true; 
                    if (!video.paused) {
                        video.pause();
                    }
                }
            """)
            
            # 2. UIボタンの状態を詳しくチェック
            try:
                play_pause = self.driver.find_element(By.ID, "play-pause-button")
                # aria-label, title 両方チェック
                label = play_pause.get_attribute("aria-label") or ""
                title = play_pause.get_attribute("title") or ""
                btn_text = label + title
                
                # 「一時停止」または「Pause」が含まれていれば、現在再生中と判断してクリック
                if any(kw in btn_text for kw in ["Pause", "一時停止", "停止"]):
                    # JS側の状態も再確認
                    is_paused = self.driver.execute_script("return document.querySelector('video') ? document.querySelector('video').paused : true")
                    if not is_paused:
                        play_pause.click()
                        print(f"[ytm_player] ボタンクリックで停止を確定しました (State: {btn_text})")
                else:
                    # 既に停止しているはず
                    pass
            except:
                pass
                
            # 最後に念押しでもう一度ミュート＆音量0
            self.driver.execute_script("try { var v = document.querySelector('video'); v.volume = 0.0; v.muted = true; } catch(e) {}")
                
        except Exception as e:
            print(f"[ytm_player] 停止処理エラー: {e}")

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    player = YTMPlayer()
    player.search_and_play("Official髭男dism Same Blue")
    time.sleep(10)
    player.stop()
