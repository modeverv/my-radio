import subprocess
import time
import chart_manager as cm

_LIBRARY_PLAYLIST = "ミュージック"
_CHART_SEARCH_ATTEMPTS = 5  # ライブラリ未収録時に試みる次のチャート曲数


class MusicPlayer:
    def __init__(self):
        self._current_track = {"title": "不明な曲", "artist": "不明なアーティスト"}

    def _run(self, script: str) -> str:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return result.stdout.strip()

    def start(self):
        self._run('tell application "Music" to activate')
        time.sleep(1)
        print("[music_player] Music.app を起動しました。")

    def _search_library(self, title: str, artist: str) -> bool:
        """タイトル+アーティストでライブラリを検索して再生。見つかればTrueを返す"""
        # 1st try: combined query → AppleScript側が両フィールドを横断検索する
        # 2nd try: title only (アーティスト名表記ゆれに備えて)
        for query in [f"{title} {artist}", title]:
            safe = query.replace('"', '\\"')
            try:
                result = self._run(f'''
                    tell application "Music"
                        set sr to search playlist "{_LIBRARY_PLAYLIST}" for "{safe}"
                        if length of sr > 0 then
                            set sound volume to 0
                            play (first item of sr)
                            return "ok"
                        end if
                        return "not found"
                    end tell
                ''')
                if result == "ok":
                    return True
            except Exception:
                continue
        return False

    def _play_track(self, track: dict):
        """チャート曲をライブラリから検索して再生。見つからなければ次の曲を試みる"""
        if self._search_library(track["title"], track["artist"]):
            self._current_track = track
            print(f"[music_player] 再生: {track['title']} / {track['artist']}")
            return

        print(f"[music_player] ライブラリ未収録: {track['title']} → 次のチャート曲を検索...")
        for _ in range(_CHART_SEARCH_ATTEMPTS):
            candidate = cm.chart_manager.next()
            if candidate and self._search_library(candidate["title"], candidate["artist"]):
                self._current_track = candidate
                print(f"[music_player] 代替再生: {candidate['title']} / {candidate['artist']}")
                return

        # 最終フォールバック: ライブラリをシャッフル再生
        print("[music_player] チャート曲が見つからず。ライブラリをシャッフル再生します。")
        self._run(f'''
            tell application "Music"
                set sound volume to 0
                set shuffle enabled to true
                play playlist "{_LIBRARY_PLAYLIST}"
            end tell
        ''')
        try:
            title = self._run('tell application "Music" to get name of current track')
            artist = self._run('tell application "Music" to get artist of current track')
            self._current_track = {"title": title, "artist": artist}
        except Exception:
            pass

    def _find_chart_playlist(self) -> str | None:
        """チャート系プレイリスト名を返す。優先度: 長い名前 > 短い名前"""
        raw = self._run('tell application "Music" to get name of every playlist')
        playlists = [p.strip() for p in raw.split(',') if p.strip()]
        matches = [p for p in playlists if any(kw in p for kw in PLAYLIST_KEYWORDS)]
        if not matches:
            return None
        # より具体的な名前（文字数多い）を優先
        return max(matches, key=len)

    def start_random_playlist(self):
        # チャートプレイリストがあれば最優先で使う（曲数が多く安定）
        playlist = self._find_chart_playlist()
        if playlist:
            print(f"[music_player] チャートプレイリスト「{playlist}」から再生します。")
            self._run(f'''
                tell application "Music"
                    set sound volume to 0
                    set shuffle enabled to true
                    play playlist "{playlist}"
                end tell
            ''')
            try:
                title = self._run('tell application "Music" to get name of current track')
                artist = self._run('tell application "Music" to get artist of current track')
                self._current_track = {"title": title, "artist": artist}
            except Exception:
                pass
            return

        # プレイリストがなければ曲単位でライブラリ検索
        track = cm.chart_manager.next()
        if track:
            self._play_track(track)
        else:
            print("[music_player] チャートデータなし。ライブラリをシャッフル再生します。")
            self._run(f'''
                tell application "Music"
                    set sound volume to 0
                    set shuffle enabled to true
                    play playlist "{_LIBRARY_PLAYLIST}"
                end tell
            ''')

    def get_current_track_info(self) -> dict:
        return self._current_track

    def next_track(self):
        track = cm.chart_manager.next()
        if track:
            self._play_track(track)
        else:
            self._run('tell application "Music" to next track')
            print("[music_player] 次の曲へスキップしました。")

    def fade_volume(self, target_volume: float, duration: float = 2.0):
        """target_volume: 0.0〜1.0"""
        target_int = int(target_volume * 100)
        steps = 20
        step_duration = round(duration / steps, 3)

        try:
            current = int(self._run('tell application "Music" to get sound volume'))
        except Exception:
            current = 0

        self._run(f'''
            tell application "Music"
                set startVol to {current}
                set endVol to {target_int}
                repeat with i from 1 to {steps}
                    set sound volume to (startVol + (endVol - startVol) * i / {steps})
                    delay {step_duration}
                end repeat
                set sound volume to {target_int}
            end tell
        ''')

    def stop(self):
        try:
            self._run('''
                tell application "Music"
                    set sound volume to 0
                    pause
                end tell
            ''')
        except Exception as e:
            print(f"[music_player] 停止エラー: {e}")

    def quit(self):
        try:
            self._run('tell application "Music" to quit')
        except Exception:
            pass
