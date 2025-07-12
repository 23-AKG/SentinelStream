import requests
import json
import os
from datetime import datetime

GITHUB_API = "https://api.github.com/repos"
RAW_URL = "https://raw.githubusercontent.com"
SAVE_PATH = "data/github_articles.json"

REPOS = {
    "MISP/misp-galaxy": "main",
     "stamparm/maltrail": "master",
     "executemalware/Malware-IOCs": "main",
    "Neo23x0/signature-base": "master"
    
}

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "SentinelStream"
}

ALLOWED_EXTENSIONS = (".md", ".txt", ".json")

def list_repo_files(owner_repo, branch):
    url = f"{GITHUB_API}/{owner_repo}/git/trees/{branch}?recursive=1"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json().get("tree", [])
    else:
        print(f"❌ Failed to list {owner_repo}: {res.status_code}")
        return []

def fetch_raw_file(owner_repo, branch, path):
    raw_url = f"{RAW_URL}/{owner_repo}/{branch}/{path}"
    res = requests.get(raw_url)
    if res.status_code == 200:
        return res.text
    else:
        print(f"⚠️ Skipped {path} — {res.status_code}")
        return None

def load_existing_articles():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_articles(data):
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def main():
    print("🐙 Fetching GitHub threat intel files...")
    all_articles = load_existing_articles()
    new_count = 0

    for repo, branch in REPOS.items():
        print(f"\n🔍 Scanning {repo}...")
        files = list_repo_files(repo, branch)

        for file in files:
            path = file.get("path", "")
            # Filter by extension
            if not path.endswith(ALLOWED_EXTENSIONS):
                continue

            # Focused folder filter for specific repos
            if repo == "MISP/misp-galaxy" and not path.startswith("clusters/"):
                continue

            if repo == "stamparm/maltrail" and not (
                path.startswith("blacklists/") or path.startswith("trails/")
            ):
                continue


            full_url = f"{RAW_URL}/{repo}/{branch}/{path}"
            if full_url in all_articles:
                continue

            content = fetch_raw_file(repo, branch, path)
            if not content:
                continue

            all_articles[full_url] = {
                "title": os.path.basename(path),
                "link": full_url,
                "published": datetime.utcnow().isoformat() + "Z",
                "content": content,
                "source": f"github:{repo}"
            }
            new_count += 1

    save_articles(all_articles)
    print(f"\n✅ Done. Fetched {new_count} new GitHub articles.")

if __name__ == "__main__":
    main()
