import feedparser
import random
from datetime import datetime

NHK_FEEDS = [
    "https://news.web.nhk/n-data/conf/na/rss/cat0.xml",
    "https://news.web.nhk/n-data/conf/na/rss/cat1.xml",
    "https://news.web.nhk/n-data/conf/na/rss/cat3.xml",
    "https://news.web.nhk/n-data/conf/na/rss/cat4.xml",
    "https://news.web.nhk/n-data/conf/na/rss/cat5.xml",
    "https://news.web.nhk/n-data/conf/na/rss/cat6.xml",
]

class NewsManager:
    def __init__(self):
        self.headlines = []
        self.current_index = 0
        # 自動実行はせず、明示的に呼び出すまで空のままにする

    def fetch_all_news(self):
        """全てのフィードからニュースを取得し、シャッフルして保持する"""
        print("[NewsManager] NHKニュースを取得中...")
        new_headlines = []
        for url in NHK_FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    if entry.title not in new_headlines:
                        new_headlines.append(entry.title)
            except Exception as e:
                print(f"[NewsManager] Warning: Failed to fetch RSS from {url}: {e}")
        
        if new_headlines:
            random.shuffle(new_headlines)
            self.headlines = new_headlines
            self.current_index = 0
            print(f"[NewsManager] {len(self.headlines)}件のニュースを読み込みました。")
        else:
            print("[NewsManager] ニュースが取得できませんでした。")

    def get_next_headlines(self, count=3) -> list:
        """リングキューのように次から次へとニュースを返す"""
        if not self.headlines:
            return ["ニュースを取得できませんでした。"]

        result = []
        for _ in range(count):
            result.append(self.headlines[self.current_index])
            self.current_index = (self.current_index + 1) % len(self.headlines)
            
            # 1周したら再シャッフルして鮮度（順序）を変える
            if self.current_index == 0:
                random.shuffle(self.headlines)
                
        return result

# グローバルインスタンス
news_manager = NewsManager()

def get_context() -> dict:
    now = datetime.now()
    hour = now.hour
    
    # Determine mood
    mood = (
        "morning_calm"    if 5  <= hour < 9  else
        "daytime_focus"   if 9  <= hour < 17 else
        "evening_relax"   if 17 <= hour < 21 else
        "late_night_chill"
    )
    
    # NewsManagerからニュースを取得
    headlines = news_manager.get_next_headlines(3)
    
    return {
        "time": now.strftime("%H:%M"),
        "day_of_week": now.strftime("%A"),
        "mood": mood,
        "headlines": headlines,
    }

if __name__ == "__main__":
    ctx = get_context()
    print(ctx)
