from feeds.fetcher import fetch_articles, save_articles

articles = fetch_articles()
print(f"✅ Fetched {len(articles)} articles.\n")

for article in articles[:3]:  # Show just first 3
    print(f"🔸 Title: {article['title']}")
    print(f"🕒 Published: {article['published']}")
    print(f"🔗 Link: {article['link']}\n")

save_articles(articles)
print("💾 Articles saved to data/raw_articles.json")
