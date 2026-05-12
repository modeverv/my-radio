import time
import context_builder
import llm_director
import tts
from ytm_player import YTMPlayer

# テスト用再生秒数（フェード時間含む）
PLAY_DURATION_SEC = 30 

# YouTube Music Player の初期化 (ブラウザ起動)
ytm = YTMPlayer()

# 直前に流れた曲の情報
last_track_info = None

def run_radio_block():
    """
    1セグメント: 
    1. 前回の曲の紹介 & ニュース (MCトーク)
    2. 次の曲へスキップ
    3. 曲再生 (PLAY_DURATION_SEC秒)
    """
    global last_track_info
    
    print(f"\n{'='*50}")
    print("[SYSTEM] 次の放送セグメントを準備中...")
    
    # --- 準備フェーズ (ニュース取得・台本生成) ---
    ctx = context_builder.get_context()
    print(f"[RADIO] @ {ctx['time']} ({ctx['day_of_week']})")
    
    # LLMに台本を依頼 (直前の曲情報があれば渡す)
    direction = llm_director.get_direction(ctx, last_track_info)
    print(f"\n[SHOW] {direction['show_title']}")
    print(f"[MC SCRIPT]\n{direction['mc_script']}\n")
    
    # --- 放送フェーズ ---

    # 1. MCトーク (音楽が止まっている状態で)
    ytm.stop()
    print("[TTS] MCトーク再生中...")
    tts.speak(direction['mc_script'])

    # 2. 曲の切り替え & 再生
    print(f"\n[PLAYER] 次の曲へ進みます...")
    ytm.next_track()
    
    # 少し待ってから曲情報を取得（UI更新待ち）
    time.sleep(2)
    current_track = ytm.get_current_track_info()
    print(f"[NOW PLAYING] {current_track['title']} / {current_track['artist']}")
    
    # フェードイン (3秒かけて 100% へ)
    ytm.fade_volume(1.0, duration=3.0)
    
    print(f"[WAIT] {PLAY_DURATION_SEC}秒間再生します...")
    # フェードアウト時間を考慮して待機
    time.sleep(max(0, PLAY_DURATION_SEC - 5.0))
    
    # フェードアウト (5秒かけて 0% へ)
    print(f"[FADE OUT] {current_track['title']}")
    ytm.fade_volume(0.0, duration=5.0)
    ytm.stop()
    
    # 今回流れた曲を記録
    last_track_info = current_track
    
    print("\n[SYSTEM] セグメント終了。")

if __name__ == "__main__":
    print("[RADIO] 起動します...")
    try:
        # 最初にランダムなプレイリストを開始
        ytm.start_random_playlist()
        # 最初の一曲目の情報を取得するために、少しだけ流して止める
        time.sleep(3)
        last_track_info = ytm.get_current_track_info()
        ytm.stop()
        
        while True:
            run_radio_block()
    except KeyboardInterrupt:
        print("\n[RADIO] 停止します")
    except Exception as e:
        print(f"[ERROR] {e}")
