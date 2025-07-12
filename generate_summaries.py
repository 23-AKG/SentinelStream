import json
import os
from datetime import datetime
from processors.ioc_extractor import extract_iocs
from processors.summarizer import summarize_article

RAW_PATH = "data/raw_articles.json"
GITHUB_PATH = "data/github_articles.json"
SUMMARY_PATH = "data/summaries.json"
PROMPT_VERSION = "v1.0"
MODEL_NAME = "llama2"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def main():
    raw_articles = load_json(RAW_PATH)
    github_articles = load_json(GITHUB_PATH)
    summaries = load_json(SUMMARY_PATH)

    # ✅ Merge both sources: raw + github
    all_articles = {**raw_articles, **github_articles}

    total = len(all_articles)
    processed = 0

    for url, article in all_articles.items():
        processed += 1
        if url in summaries:
            print(f"🔄 [{processed}/{total}] Skipping already summarized: {article['title']}")
            continue

        # ✅ Skip LLM summarization for raw IOC dumps (e.g., maltrail .txt files)
        if article.get("source", "").startswith("github:stamparm/maltrail") and article["title"].endswith(".txt"):
            print(f"📄 [{processed}/{total}] Skipping summarization for raw IOC file: {article['title']}")
            summary_text = "⚠️ Skipped LLM summarization — IOC dump file"
        else:
            print(f"🧠 [{processed}/{total}] Summarizing: {article['title']}")
            summary_text = summarize_article(
                text=article.get("content", ""),
                title=article.get("title", ""),
                source_url=url
            )

        iocs = extract_iocs(article.get("content", ""))

        summaries[url] = {
            "title": article.get("title", ""),
            "link": url,
            "summary": summary_text,
            "iocs": iocs,
            "llm_meta": {
                "model": MODEL_NAME,
                "prompt_version": PROMPT_VERSION,
                "generated_on": datetime.utcnow().isoformat()
            }
        }

        save_json(summaries, SUMMARY_PATH)

    print(f"\n✅ Completed: {processed} articles processed.")

if __name__ == "__main__":
    main()
