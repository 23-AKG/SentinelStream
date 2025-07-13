import json
import os

SUMMARY_PATH = "data/summaries.json"
OUTPUT_PATH = "data/ioc_index.json"

def generate_ioc_index(summary_path, output_path):
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Missing file: {summary_path}")

    with open(summary_path, "r") as f:
        summaries = json.load(f)

    index = {}
    for url, entry in summaries.items():
        iocs = entry.get("iocs", {})
        ipv4 = iocs.get("ipv4", [])
        urls = iocs.get("url", [])
        hashes = iocs.get("hash", [])

        if ipv4 or urls or hashes:
            index[url] = {
                "ipv4": ipv4,
                "url": urls,
                "hash": hashes
            }

    with open(output_path, "w") as f:
        json.dump(index, f, indent=2)

    print(f"✅ IOC index created at {output_path} with {len(index)} articles.")

if __name__ == "__main__":
    generate_ioc_index(SUMMARY_PATH, OUTPUT_PATH)