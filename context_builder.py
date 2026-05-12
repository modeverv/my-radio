import feedparser
from datetime import datetime

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://www3.nhk.or.jp/rss/news/cat6.xml",
]

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
    
    # Fetch headlines
    headlines = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            # Take up to 2 items from each feed
            count = 0
            for entry in feed.entries:
                if count >= 2:
                    break
                headlines.append(entry.title)
                count += 1
        except Exception as e:
            print(f"[context_builder] Warning: Failed to fetch RSS from {url}: {e}")
            
    # Limit total headlines to 6
    headlines = headlines[:6]
    
    return {
        "time": now.strftime("%H:%M"),
        "day_of_week": now.strftime("%A"),
        "mood": mood,
        "headlines": headlines,
    }

if __name__ == "__main__":
    ctx = get_context()
    print(ctx)
