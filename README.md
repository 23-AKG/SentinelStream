# 🛡️ SentinelStream

**Real-time Threat Intelligence Aggregator with AI Summaries and IOC Extraction**

---

## 🔍 Overview

SentinelStream is a full-stack threat intelligence dashboard built to empower SOC teams, threat researchers, and analysts. It automatically pulls data from open-source intelligence feeds and GitHub repositories, summarizes key threat findings using LLMs, and extracts Indicators of Compromise (IOCs) like IPs, hashes, URLs, and domains — all through a simple, interactive UI.

---

## ✨ Features

- 📥 **Live Feed Aggregation** from curated GitHub & OSINT sources
- 🧠 **AI Summaries** using LLaMA 2 and Gemini LLMs
- 🧨 **IOC Extraction** (IPv4, URLs, file hashes)
- 🔍 **IOC Search** in dedicated threat feeds
- 📎 **Downloadable IOC Reports** for any article
- 📝 **Custom Article Analyzer** *(Beta)* — analyze your own links
- ⚙️ **Pipeline Rerun** to refresh all data with one click

---

## 📂 Folder Structure

```
sentinelstream/
├── data/                        # Data inputs and outputs
│   ├── ioc_index.json
│   ├── ip_blocklist.txt
│   ├── md5.txt
│   ├── osint.txt
│   ├── raw_articles.json
│   ├── sha.txt
│   ├── summaries.json
│   ├── url.txt
│
├── feeds/                      # Feed collectors and source config
│   ├── fetcher.py
│   ├── github_fetcher.py
│   ├── sources.json
│
├── processors/                # Processing logic (modular)
│   ├── gemini_summarizer.py
│   ├── ioc_extractor.py
│   ├── scorer.py
│   ├── summarizer.py
│
├── .gitignore
├── APNotes.json               # Domain-specific intelligence notes
├── generate_ioc_index.py
├── generate_summaries.py
├── merge_github_articles.py
├── split_github_articles.py
├── test_feed.py
├── test_ioc.py
├── test_summary.py
├── ui.py                      # Frontend using Gradio
├── requirements.txt
├── README.md

```

---

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sentinelstream.git
cd sentinelstream
```

### 2. Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add Gemini API Key
Inside `processors/gemini_summarizer.py`, directly paste your key:
```python
API_KEY = "your-gemini-api-key"
```

### 4. Run the App
```bash
python ui.py
```
---

## 📌 Usage

- **Feed Overview** — Explore threat feeds and IOCs
- **Search IOC** — Enter an IP, URL, or hash to check
- **AI Cards** — View summaries + download IOCs
- **Analyze Article** *(Beta)* — Paste any link for processing
- **Pipeline Refresh** — Re-fetch all sources and regenerate data

---
## 📽️ Demo Video

[![Watch the demo](https://img.youtube.com/vi/yzgUi-iq5Xk/0.jpg)](([https://youtu.be/yzgUi-iq5Xk](https://www.youtube.com/watch?v=yzgUi-iq5Xk))

---

## ⚠️ Limitations

- The **Analyze My Article** tab is under development; summarization and IOC extraction are partially functional.
- Flat-file JSON storage (Didn't go with a DB for the MVP stage) — not optimized for scale.
- Requires manual Gemini API key insertion for now.

---

## 🌱 Future Improvements

- Fully stabilize user article analysis pipeline.
- Add backend database (SQLite or MongoDB).
- Introduce API access and login-based access control.
- Improve UI styling and responsiveness (React/Next.js)

---

## 🤝 Contribution

Contributions welcome! Feel free to open issues, submit PRs, or suggest features.

---

## 🙏 Acknowledgments

- [Gradio](https://gradio.app/)
- [Ollama](https://ollama.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Stamparm’s Maltrail](https://github.com/stamparm/maltrail)
