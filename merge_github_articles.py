# merge_github_articles.py
import json
import os
import glob

PART_PATTERN = "data/github_articles_part_*.json"
MERGED_FILE = "data/github_articles.json"

def merge_and_cleanup():
    merged = {}
    part_files = sorted(glob.glob(PART_PATTERN))

    for part_file in part_files:
        with open(part_file, "r") as f:
            part_data = json.load(f)
            merged.update(part_data)
        print(f"🔗 Merged: {part_file}")

    with open(MERGED_FILE, "w") as f:
        json.dump(merged, f, indent=2)

    # Cleanup
    for part_file in part_files:
        os.remove(part_file)
        print(f"🗑️ Deleted: {part_file}")

    print(f"\n✅ All fragments merged into {MERGED_FILE} with {len(merged)} entries.")

if __name__ == "__main__":
    merge_and_cleanup()
