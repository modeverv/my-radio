from ytmusicapi import YTMusic
import random
import os

def get_yt_client():
    # 認証なしでも検索経由で十分な情報が取得できるため、シンプルに初期化します
    return YTMusic()

def get_candidate_tracks(mood: str = None) -> list[dict]:
    yt = get_yt_client()
    
    # 試行2: 日本のトップ100プレイリスト (ユーザー様提供の最新URL)
    try:
        playlist_id = 'OLAK5uy_nMa6r07BbcC_Q8PrrS1CVHH2aGJRIkWu0'
        playlist = yt.get_playlist(playlist_id, limit=500)
        chart_songs = playlist.get('tracks', [])
        if chart_songs:
            return _process_songs(chart_songs, "Playlist")
    except:
        pass

    # 試行1: 日本のチャート取得
    try:
        charts = yt.get_charts(country='JP')
        chart_songs = charts.get('songs', {}).get('items', [])
        if chart_songs:
            return _process_songs(chart_songs, "Charts")
    except:
        pass


    # 試行3: 検索によるフォールバック（最も確実）
    try:
        print("[youtube] チャート取得不能のため、検索で代用します...")
        search_results = yt.search("日本 ヒット", filter="songs", limit=30)
        if search_results:
            return _process_songs(search_results, "Search")
    except Exception as e:
        print(f"[youtube] 検索にも失敗しました: {e}")

    return [{"title": "Jazz", "artist": "Standard", "album": ""}]

def _process_songs(songs: list, source: str) -> list[dict]:
    print(f"[youtube] {source} より {len(songs)} 件取得しました。")
    tracks = []
    for s in songs:
        title = s.get('title', 'Unknown Title')
        artists = s.get('artists', [])
        artist_name = artists[0].get('name') if artists else "Unknown Artist"
        print(f"  - {title} / {artist_name}")
        tracks.append({
            "title": title,
            "artist": artist_name,
            "album": s.get('album', {}).get('name', "") if s.get('album') else ""
        })
    
    if len(tracks) > 15:
        return random.sample(tracks, 15)
    return tracks

if __name__ == "__main__":
    get_candidate_tracks()
