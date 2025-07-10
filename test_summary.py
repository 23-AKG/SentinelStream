import json
from processors.summarizer import summarize_article  # adjust path if needed

with open("data/raw_articles.json", "r") as f:
    articles = json.load(f)

for article in articles[:3]:  # Try first 3 for now
    title = article.get("title", "Untitled")
    link = article.get("link", "N/A")
    content = article.get("content", "")

    print(f"\n🔹 {title}")
    print(f"🔗 {link}")

    summary = summarize_article(text=content, title=title, source_url=link)
    print("📝 Summary:")
    print(summary)
