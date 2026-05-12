import urllib.request
import json
import random

_ITUNES_JP_TOP100 = "https://itunes.apple.com/jp/rss/topsongs/limit=100/json"


class ChartManager:
    def __init__(self):
        self._tracks = []
        self._index = 0

    def fetch(self):
        print("[ChartManager] iTunes JP Top 100 を取得中...")
        try:
            with urllib.request.urlopen(_ITUNES_JP_TOP100, timeout=10) as r:
                data = json.load(r)
            self._tracks = [
                {
                    "title":     e["im:name"]["label"],
                    "artist":    e["im:artist"]["label"],
                    "itunes_id": e["id"]["attributes"]["im:id"],
                }
                for e in data["feed"]["entry"]
            ]
            random.shuffle(self._tracks)
            self._index = 0
            print(f"[ChartManager] {len(self._tracks)}曲を取得しました。")
        except Exception as e:
            print(f"[ChartManager] 取得失敗: {e}")

    def next(self) -> dict | None:
        if not self._tracks:
            return None
        track = self._tracks[self._index]
        self._index = (self._index + 1) % len(self._tracks)
        if self._index == 0:
            random.shuffle(self._tracks)
        return track

    def peek_top(self, n: int = 5) -> list:
        return self._tracks[:n]


chart_manager = ChartManager()


if __name__ == "__main__":
    chart_manager.fetch()
    for t in chart_manager.peek_top(10):
        print(f"  {t['title']} / {t['artist']}  (id={t['itunes_id']})")
