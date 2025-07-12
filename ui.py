import json
import os
import re
import gradio as gr
from datetime import datetime
from collections import defaultdict

SUMMARY_PATH = "data/summaries.json"

FEED_FILES = {
    "OSINT Threat Feed": "data/osint.txt",
    "C2 Hunt Feed": "data/c2.txt",
    "IP Blocklist": "data/ip_blocklist.txt",
    "Domain Blocklist": "data/domain_blocklist.txt",
    "MD5 Hash Blocklist": "data/md5.txt",
    "URL Blocklist": "data/url.txt",
    "Bitcoin Address Intel": "data/bitcoin.txt",
    "SHA File Hash Blocklist": "data/sha.txt"
}

# ================== Utility Functions ===================
def load_feed_content_partial(feature_name):
    path = FEED_FILES.get(feature_name)
    if not path or not os.path.exists(path):
        return f"❌ No data found for {feature_name}."
    with open(path, "r") as f:
        lines = f.readlines()
    top_50 = lines[:50]
    return f"### {feature_name} (Top 50 IOCs)\n\n```\n" + "".join(top_50) + "```"

def load_feed_full(feature_name):
    path = FEED_FILES.get(feature_name)
    if not path or not os.path.exists(path):
        return f"❌ No data found for {feature_name}."
    with open(path, "r") as f:
        data = f.read()
    return f"### Full {feature_name}\n\n```\n{data}\n```"

def check_if_malicious(selected_feed, user_input):
    path = FEED_FILES.get(selected_feed)
    if not path or not os.path.exists(path):
        return "❌ Feed file not found."
    with open(path, "r") as f:
        contents = f.read()
    if user_input.strip() in contents:
        return f"🚨 `{user_input}` is **Malicious** according to {selected_feed}!"
    else:
        return f"✅ `{user_input}` is **Safe** in {selected_feed}."

# ================ IOC Summary Cards ================
def load_summaries():
    if not os.path.exists(SUMMARY_PATH):
        return {}
    with open(SUMMARY_PATH, "r") as f:
        return json.load(f)

def get_source_tag(link):
    return "GitHub" if "github" in link else "RSS"

def group_iocs(iocs):
    groups = defaultdict(list)
    for ioc in iocs:
        if re.match(r"\b\d{1,3}(\.\d{1,3}){3}\b", ioc):
            groups["IP"].append(ioc)
        elif re.match(r"^https?://", ioc):
            groups["URL"].append(ioc)
        elif re.match(r"^[a-fA-F0-9]{32,}$", ioc):
            groups["Hash"].append(ioc)
        else:
            groups["Other"].append(ioc)
    return groups

def render_summary_cards(query, sort_order, group_toggle):
    summaries = load_summaries()
    entries = []

    for url, entry in summaries.items():
        combined_text = (entry["title"] + entry["summary"]).lower()
        if query and query.lower() not in combined_text:
            continue
        entries.append((url, entry))

    reverse = sort_order == "Newest First"
    entries.sort(key=lambda x: x[1]["llm_meta"]["generated_on"], reverse=reverse)

    if not entries:
        return "🚫 No matching summaries found."

    rendered = ""
    for url, entry in entries:
        title = entry["title"]
        summary = entry["summary"]
        source = get_source_tag(entry["link"])
        date = entry["llm_meta"]["generated_on"].split("T")[0]
        iocs = entry["iocs"]

        if iocs:
            if group_toggle:
                grouped = group_iocs(iocs)
                ioc_html = "".join(
                    f"<details><summary>{k} ({len(v)})</summary><ul>" +
                    "".join(f"<li>{item}</li>" for item in v) +
                    "</ul></details>" for k, v in grouped.items()
                )
            else:
                ioc_html = "<ul>" + "".join(f"<li>{ioc}</li>" for ioc in iocs) + "</ul>"
            ioc_section = f"<div style='margin-top: 8px; color: limegreen; font-weight: bold;'>✅ IOCs Found</div>{ioc_html}"
        else:
            ioc_section = "<div style='margin-top: 8px; color: gray;'>❌ No IOCs Found</div>"

        card_html = f"""
        <div style='padding: 14px; border-radius: 12px; background: #1f1f1f; margin-bottom: 16px; box-shadow: 0 0 8px rgba(0,0,0,0.5);'>
            <h3 style='margin-bottom: 0.2em;'>{title}</h3>
            <div style='font-size: 0.9em; color: gray;'>{date} • <span style='color: orange;'>{source}</span></div>
            <p style='margin-top: 1em;'>{summary}</p>
            {ioc_section}
            <div style='margin-top: 10px;'><a href="{url}" target="_blank" style='color: #4faaff;'>🔗 View Original</a></div>
        </div>
        """
        rendered += card_html

    return rendered

def refresh_pipeline():
    os.system("python3 feeds/fetcher.py && python3 feeds/github_fetcher.py && python3 generate_summaries.py")
    return "✅ Pipeline re-run complete."

# =================== UI =======================
def build_ui():
    with gr.Blocks() as app:
        gr.Markdown("## 🛡️ SentinelStream Dashboard")
        gr.Markdown("Real-time AI summaries and threat intelligence feed viewer")

        with gr.Tab("📌 Feed Overview"):
            feed_output = gr.Markdown("Click a feature to view top IOCs.")

            with gr.Row():
                b1 = gr.Button("OSINT Threat Feed")
                b2 = gr.Button("C2 Hunt Feed")
                b3 = gr.Button("IP Blocklist")
                b4 = gr.Button("Domain Blocklist")
            with gr.Row():
                b5 = gr.Button("MD5 Hash Blocklist")
                b6 = gr.Button("URL Blocklist")
                b7 = gr.Button("Bitcoin Address Intel")
                b8 = gr.Button("SHA File Hash Blocklist")

            more_input = gr.Textbox(visible=False)
            more_button = gr.Button("Show Full Feed in New Tab")
            full_output = gr.Textbox(visible=False)

            # Hook feed buttons
            for button, name in zip([b1, b2, b3, b4, b5, b6, b7, b8], FEED_FILES.keys()):
                button.click(load_feed_content_partial, inputs=[gr.Textbox(value=name, visible=False)], outputs=feed_output)
                button.click(fn=lambda x: x, inputs=[gr.Textbox(value=name, visible=False)], outputs=more_input)

            more_button.click(load_feed_full, inputs=more_input, outputs=full_output)

        with gr.Tab("📖 Full Feed View"):
            gr.Markdown("Below is the full feed content of the last feature you selected:")
            full_view = gr.Markdown()
            more_button.click(load_feed_full, inputs=more_input, outputs=full_view)

        with gr.Tab("🔍 Search IOC in Feed"):
            gr.Markdown("Check if your IP, URL, hash, or domain is malicious")
            selected_feed = gr.Dropdown(choices=list(FEED_FILES.keys()), label="Select Feed")
            user_input = gr.Textbox(label="Enter IOC to search (e.g. IP, hash, URL)")
            search_btn = gr.Button("Check Now")
            result = gr.Markdown()
            search_btn.click(check_if_malicious, inputs=[selected_feed, user_input], outputs=result)

        with gr.Tab("🧠 AI Summary Cards"):
            with gr.Row():
                query = gr.Textbox(placeholder="Search by keyword, threat actor, or IOC", label="Search", scale=2)
                sort = gr.Radio(choices=["Newest First", "Oldest First"], value="Newest First", label="Sort")
                group = gr.Checkbox(label="Group IOCs by type (IP, URL, Hash)")

            results = gr.HTML()
            query.change(render_summary_cards, inputs=[query, sort, group], outputs=results)
            sort.change(render_summary_cards, inputs=[query, sort, group], outputs=results)
            group.change(render_summary_cards, inputs=[query, sort, group], outputs=results)

        with gr.Accordion("🔁 Refresh Feeds + Re-Summarize", open=False):
            gr.Markdown("Will re-fetch feeds and re-run summaries using Ollama.")
            refresh_btn = gr.Button("🚀 Run Pipeline")
            refresh_btn.click(fn=refresh_pipeline, outputs=[])

        app.load(render_summary_cards, inputs=[query, sort, group], outputs=results)

    return app

if __name__ == "__main__":
    build_ui().launch()
