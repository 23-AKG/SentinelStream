<<<<<<< HEAD
# split_github_articles.py
import json
import os

INPUT_FILE = "data/github_articles.json"
OUTPUT_DIR = "data"
MAX_FILE_SIZE_MB = 45  # GitHub max is 100MB, keep a buffer

def get_size_mb(obj):
    return len(json.dumps(obj).encode("utf-8")) / (1024 * 1024)

def split_json(input_path, output_dir, max_mb):
    with open(input_path, "r") as f:
        data = json.load(f)

    parts = []
    current_part = {}
    current_size = 0

    for key, value in data.items():
        entry_size = get_size_mb({key: value})
        if current_size + entry_size > max_mb:
            parts.append(current_part)
            current_part = {}
            current_size = 0

        current_part[key] = value
        current_size += entry_size

    if current_part:
        parts.append(current_part)

    for i, part in enumerate(parts, start=1):
        part_path = os.path.join(output_dir, f"github_articles_part_{i}.json")
        with open(part_path, "w") as f:
            json.dump(part, f, indent=2)
        print(f"✅ Saved: {part_path} ({get_size_mb(part):.2f} MB)")

if __name__ == "__main__":
    split_json(INPUT_FILE, OUTPUT_DIR, MAX_FILE_SIZE_MB)
=======
# split_github_articles.py
import json
import os

INPUT_FILE = "data/github_articles.json"
OUTPUT_DIR = "data"
MAX_FILE_SIZE_MB = 45  # GitHub max is 100MB, keep a buffer

def get_size_mb(obj):
    return len(json.dumps(obj).encode("utf-8")) / (1024 * 1024)

def split_json(input_path, output_dir, max_mb):
    with open(input_path, "r") as f:
        data = json.load(f)

    parts = []
    current_part = {}
    current_size = 0

    for key, value in data.items():
        entry_size = get_size_mb({key: value})
        if current_size + entry_size > max_mb:
            parts.append(current_part)
            current_part = {}
            current_size = 0

        current_part[key] = value
        current_size += entry_size

    if current_part:
        parts.append(current_part)

    for i, part in enumerate(parts, start=1):
        part_path = os.path.join(output_dir, f"github_articles_part_{i}.json")
        with open(part_path, "w") as f:
            json.dump(part, f, indent=2)
        print(f"✅ Saved: {part_path} ({get_size_mb(part):.2f} MB)")

if __name__ == "__main__":
    split_json(INPUT_FILE, OUTPUT_DIR, MAX_FILE_SIZE_MB)
>>>>>>> origin/github-threat-intel-repos
