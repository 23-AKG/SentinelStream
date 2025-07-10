from feeds.fetcher import fetch_articles, save_articles
from processors.ioc_extractor import extract_iocs

articles = fetch_articles()

for article in articles:
    article["iocs"] = extract_iocs(article.get("content", ""))

save_articles(articles)
print("✅ Fetched and extracted IOCs. Saved to data/raw_articles.json")

# Preview a few
for a in articles[:2]:
    print(f"\n🔹 {a['title']}")
    print("  IOCs:", a["iocs"])
