import time
import threading
import context_builder
import llm_director
import tts
from ytm_player import YTMPlayer

# テスト用再生秒数（フェード時間含む）
PLAY_DURATION_SEC = 30 

# YouTube Music Player の初期化 (ブラウザ起動)
ytm = YTMPlayer()

# 次のセグメント用の準備データ
next_segment_data = {
    "script": None,
    "ready": False,
    "lock": threading.Lock()
}

def prepare_next_mc_talk(track_info):
    """バックグラウンドで次のMCトークを準備する"""
    global next_segment_data
    try:
        print("[SYSTEM] バックグラウンドでコンテキスト取得とMCトーク生成を開始...")
        # 重い処理（ネットワークI/O）をすべてスレッド内で実行
        context = context_builder.get_context()
        direction = llm_director.get_direction(context, track_info)

        with next_segment_data["lock"]:
            next_segment_data["script"] = direction["mc_script"]
            next_segment_data["show_title"] = direction["show_title"]
            next_segment_data["ready"] = True
            next_segment_data["path"] = tts.make(direction["mc_script"])
        print("[SYSTEM] 次のMCトークの準備が完了しました。")
    except Exception as e:
        print(f"[ERROR] バックグラウンド準備中にエラー: {e}")

first = True

def run_radio_block():
    """
    1セグメントの進行
    """
    global last_track_info, next_segment_data, first

    # 1. 前のループで準備されたMCトークを再生
    path = ""
    while True:
        with next_segment_data["lock"]:
            if next_segment_data["ready"]:
                script = next_segment_data["script"]
                path = next_segment_data["path"]
                show_title = next_segment_data["show_title"]
                next_segment_data["ready"] = False
                break
        time.sleep(0.5)

    print(f"\n{'='*50}")
    print(f"[SHOW] {show_title}")

    ytm.stop()

    print("[TTS] MCトーク再生中...")
    print(script)
    tts.speak(path)

    # 2. 曲の切り替え & 再生開始
    if first:
        first = False
        # 1. 初期化: YTM開始
        ytm.start_random_playlist()
        time.sleep(5) # ページ遷移と再生開始を待つ
        # 最初の一曲目の情報を取得
        initial_track = ytm.get_current_track_info()
        print(f"[SYSTEM] 初期曲を検出: {initial_track['title']}")
        current_track = ytm.get_current_track_info()
    else:
        print("\n[PLAYER] 次の曲へ進みます...")
        ytm.next_track()
        time.sleep(2)
        current_track = ytm.get_current_track_info()
        print(f"[NOW PLAYING] {current_track['title']} / {current_track['artist']}")
    
    # フェードイン
    ytm.fade_volume(1.0, duration=3.0)
    
    # --- 重要: 音楽再生中に「次のセグメント」の準備を開始する ---
    # get_context() もスレッド内に移動し、メインスレッドの負荷を最小限にする
    prep_thread = threading.Thread(target=prepare_next_mc_talk, args=(current_track,))
    prep_thread.setDaemon(True) # プログラム終了時にスレッドも終了するように
    prep_thread.start()
    # 音楽再生待機
    print(f"[WAIT] {PLAY_DURATION_SEC}秒間再生します (この間に次を準備)...")
    time.sleep(max(0, PLAY_DURATION_SEC - 5.0))
    # フェードアウト
    print(f"[FADE OUT] {current_track['title']}")
    ytm.fade_volume(0.0, duration=5.0)
    ytm.stop()

if __name__ == "__main__":
    print("[RADIO] 起動します...")
    try:
        # 0. ニュースを一括取得 (起動時に1回だけ)
        context_builder.news_manager.fetch_all_news()

        ytm.start()

        # 2. 初回のMCトークを準備 (ここは初回のみ同期で実行して確実に準備する)
        # ただし、直前の曲として initial_track を渡して紹介してもらう
        prepare_next_mc_talk("")

        print("[SYSTEM] 準備完了。放送を開始します。")
        while True:
            run_radio_block()
    except KeyboardInterrupt:
        print("\n[RADIO] 停止します")
    except Exception as e:
        print(f"[ERROR] {e}")

