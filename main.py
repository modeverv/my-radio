import time
import context_builder
import llm_director
import tts
from ytm_player import YTMPlayer
import youtube_client

# テスト用再生秒数（フェード時間含む）
PLAY_DURATION_SEC = 30 

# YouTube Music Player の初期化 (ブラウザ起動)
ytm = YTMPlayer()

def run_radio_block():
    """
    1セグメント: MCトーク(ニュース要約) -> 曲1 -> 曲2 の流れを実行
    """
    
    # --- 準備フェーズ (ニュース取得・台本生成) ---
    print(f"\n{'='*50}")
    print("[SYSTEM] 次の放送セグメントを準備中...")
    
    ctx = context_builder.get_context()
    print(f"[RADIO] @ {ctx['time']} ({ctx['day_of_week']})")
    print(f"  mood: {ctx['mood']}")
    
    candidates = youtube_client.get_candidate_tracks(ctx['mood'])
    
    direction = llm_director.get_direction(ctx, candidates)
    print(f"\n[SHOW] {direction['show_title']}")
    print(f"[MC SCRIPT]\n{direction['mc_script']}\n")
    
    # --- 放送フェーズ ---

    # 1. MCトーク
    # トーク前に前回の曲を確実に停止
    ytm.stop()
    print("[TTS] MCトーク再生中...")
    # Janomeによる自動形態素解析を経てVOICEVOXで再生
    tts.speak(direction['mc_script'])

    # 2. 曲再生 (最大2曲)
    play_count = 0
    for track in direction['playlist']:
        if play_count >= 2:
            break
            
        query = f"{track['title']} {track['artist']}"
        print(f"\n[PLAYER] 次の曲: {query}")
        
        # ytm_player.search_and_play で再生 (内部で音量を0にセット)
        success = ytm.search_and_play(query)
        if not success:
            print(f"[PLAYER] スキップします: {query}")
            continue
            
        print(f"[NOW PLAYING] {track['title']} / {track['artist']}")
        
        # フェードイン (3秒かけて 100% へ)
        ytm.fade_volume(1.0, duration=3.0)
        
        print(f"[WAIT] {PLAY_DURATION_SEC}秒間再生します...")
        # フェードアウト時間を考慮して待機
        time.sleep(max(0, PLAY_DURATION_SEC - 5.0))
        
        # フェードアウト (5秒かけて 0% へ)
        print(f"[FADE OUT] {track['title']}")
        ytm.fade_volume(0.0, duration=5.0)
        
        play_count += 1
    
    print("\n[SYSTEM] セグメント終了。次のニュースへ...")

if __name__ == "__main__":
    print("[RADIO] 起動します...")
    while True:
        try:
            run_radio_block()
        except KeyboardInterrupt:
            print("\n[RADIO] 停止します")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)  # エラー時は5秒待って再試行
