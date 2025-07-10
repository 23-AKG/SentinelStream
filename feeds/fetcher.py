import feedparser
import json
import os
from datetime import datetime

RAW_PATH = "data/raw_articles.json"
FEED_LIST = "feeds/sources.json"

def load_feed_urls(file_path=FEED_LIST):
    with open(file_path, "r") as f:
        return json.load(f)

def load_existing_articles(path=RAW_PATH):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                print("⚠️ Existing raw_articles.json is not a dictionary. Reinitializing.")
                return {}
        except json.JSONDecodeError:
            print("❌ Error parsing raw_articles.json. Reinitializing.")
            return {}

def fetch_articles():
    feeds = load_feed_urls()
    existing = load_existing_articles()
    new_articles = 0

    for feed_url in feeds:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries:
            url = entry.get("link")
            if not url or url in existing:
                continue  # Skip already saved article

            content = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
            article = {
                "title": entry.get("title", "Untitled"),
                "link": url,
                "published": entry.get("published", datetime.utcnow().isoformat()),
                "content": content,
                "source": feed_url
            }

            existing[url] = article
            new_articles += 1

    return existing, new_articles

def save_articles(articles, path=RAW_PATH):
    with open(path, "w") as f:
        json.dump(articles, f, indent=2)

if __name__ == "__main__":
    print("📡 Fetching articles...")
    data, added = fetch_articles()
    save_articles(data)
    print(f"✅ Fetched and saved {len(data)} articles ({added} new).")
