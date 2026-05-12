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
        chrome_options.add_experimental_option("detach", True)
        
        project_dir = os.path.dirname(os.path.abspath(__file__))
        user_data_dir = os.path.join(project_dir, "chrome_profile")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
            
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-allow-origins=*")
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
        # JavaScriptでフェード処理を実行
        # setIntervalを使って、ブラウザの内部時計で滑らかに変化させます
        script = f"""
        var target = {target_volume};
        var duration = {duration * 1000};
        var video = document.querySelector('video');
        if (!video) return;

        var startVolume = video.volume;
        var startTime = performance.now();

        var fade = setInterval(function() {{
            var elapsed = performance.now() - startTime;
            var progress = elapsed / duration;

            if (progress >= 1) {{
                video.volume = target;
                clearInterval(fade);
            }} else {{
                video.volume = startVolume + (target - startVolume) * progress;
            }}
        }}, 50); // 50msごとに更新
        """
        self.driver.execute_script(script)

        # Python側ではフェードが終わるまで待機（同期を保つため）
        time.sleep(duration)
    except Exception as e:
        print(f"[ytm_player] フェード実行エラー: {e}")


    def search_and_play(self, query: str) -> bool:
        """現在のコンテキスト(プレイリスト内か検索結果か)を判断して再生する"""
        try:
            # 音量を0にしておく
            try:
                self.driver.execute_script("document.querySelector('video').volume = 0.0")
            except:
                pass

            current_url = self.driver.current_url
            song_title = query.split(' / ')[0].split(' - ')[0].strip()

            # 1. プレイリスト/チャート画面にいる場合
            if "list=" in current_url:
                print(f"[ytm_player] プレイリスト内で探しています: {song_title}")
                if self._play_from_list(song_title):
                    return True
                print(f"[ytm_player] プレイリスト内に見つかりません。検索に切り替えます。")

            # 2. 検索を実行して再生する
            return self._execute_search_and_play(query)

        except Exception as e:
            print(f"[ytm_player] 再生処理でエラーが発生しました: {e}")
            return False

    def _play_from_list(self, song_title: str) -> bool:
        """現在のページ（プレイリスト）内から曲を探してクリックする"""
        try:
            wait = WebDriverWait(self.driver, 5)
            # タイトル要素を検索 (containsを使うことで部分一致に対応)
            xpath = f"//yt-formatted-string[contains(@class, 'title') and contains(text(), '{song_title}')]"
            song_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            
            # 親の行要素を取得してスクロール
            parent_row = song_element.find_element(By.XPATH, "./ancestor::ytmusic-responsive-list-item-renderer")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent_row)
            time.sleep(1)
            
            # ホバーして再生ボタンをクリック
            actions = ActionChains(self.driver)
            actions.move_to_element(parent_row).perform()
            time.sleep(0.5)
            
            play_button = parent_row.find_element(By.CSS_SELECTOR, "ytmusic-play-button-renderer")
            self.driver.execute_script("arguments[0].click();", play_button)
            
            print(f"[ytm_player] プレイリストから再生開始: {song_title}")
            return True
        except:
            return False

    def _execute_search_and_play(self, query: str) -> bool:
        """グローバル検索を実行して再生する"""
        try:
            print(f"[ytm_player] グローバル検索を実行中: {query}")
            wait = WebDriverWait(self.driver, 10)
            
            # 検索ボタンをクリックして入力欄を出す
            try:
                search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytmusic-search-box")))
                search_button.click()
            except:
                pass
                
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.ytmusic-search-box")))
            search_input.clear()
            search_input.send_keys(query)
            search_input.send_keys(Keys.ENTER)
            
            time.sleep(3) # 結果反映待ち
            
            # A: トップ結果の大きなボタン
            try:
                top_play_button = self.driver.find_element(By.XPATH, "//ytmusic-card-shelf-renderer//ytmusic-play-button-renderer")
                self.driver.execute_script("arguments[0].click();", top_play_button)
                print(f"[ytm_player] 検索トップ結果から再生開始")
                return True
            except:
                pass
                
            # B: 検索結果リストの最初のボタン
            try:
                play_button = self.driver.find_element(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer ytmusic-play-button-renderer")
                self.driver.execute_script("arguments[0].click();", play_button)
                print(f"[ytm_player] 検索リストから再生開始")
                return True
            except:
                pass
            
            return False
        except Exception as e:
            print(f"[ytm_player] 検索再生に失敗しました: {e}")
            return False

    def stop(self):
        """再生を停止し、音量を完全に0にする"""
        try:
            # まず音量を0にする
            self.driver.execute_script("try { document.querySelector('video').volume = 0.0; } catch(e) {}")
            
            # 再生中であれば一時停止ボタンを押す
            play_pause = self.driver.find_element(By.ID, "play-pause-button")
            if "Pause" in play_pause.get_attribute("aria-label"):
                play_pause.click()
                print("[ytm_player] 再生を停止しました。")
        except Exception as e:
            # 停止に失敗しても、音量だけは0にする試行
            try:
                self.driver.execute_script("document.querySelector('video').volume = 0.0")
            except:
                pass

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    player = YTMPlayer()
    player.search_and_play("Official髭男dism Same Blue")
    time.sleep(10)
    player.stop()
