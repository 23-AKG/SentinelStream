import json
import os
import gradio as gr
from datetime import datetime

SUMMARY_PATH = "data/summaries.json"

def load_summaries():
    with open(SUMMARY_PATH, "r") as f:
        return json.load(f)

def get_source_tag(link):
    if "github" in link:
        return "GitHub"
    return "RSS"

def group_iocs(iocs):
    from collections import defaultdict
    import re
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

    # Filter
    for url, entry in summaries.items():
        combined_text = (entry["title"] + entry["summary"]).lower()
        if query and query.lower() not in combined_text:
            continue
        entries.append((url, entry))

    # Sort
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

        # IOC badge
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
            ioc_section = f"""
            <div style='margin-top: 8px; color: limegreen; font-weight: bold;'>✅ IOCs Found</div>
            {ioc_html}
            """
        else:
            ioc_section = "<div style='margin-top: 8px; color: gray;'>❌ No IOCs Found</div>"

        # Render card
        card_html = f"""
        <div style='padding: 14px; border-radius: 12px; background: #1f1f1f; margin-bottom: 16px; box-shadow: 0 0 8px rgba(0,0,0,0.5);'>
            <h3 style='margin-bottom: 0.2em;'>{title}</h3>
            <div style='font-size: 0.9em; color: gray;'>{date} • <span style='color: orange;'>{source}</span></div>
            <p style='margin-top: 1em;'>{summary}</p>
            {ioc_section}
            <div style='margin-top: 10px;'>
                <a href="{url}" target="_blank" style='color: #4faaff;'>🔗 View Original</a>
            </div>
        </div>
        """
        rendered += card_html

    return rendered

def refresh_pipeline():
    os.system("python3 feeds/fetcher.py && python3 feeds/github_fetcher.py && python3 generate_summaries.py")
    return "✅ Pipeline re-run complete."

def build_ui():
    with gr.Blocks() as app:
        gr.Markdown("## 🛡️ SentinelStream Dashboard")
        gr.Markdown("Real-time AI summaries of cyber threat intel from curated feeds.")

        with gr.Row():
            query = gr.Textbox(placeholder="Search by keyword, threat actor, or IOC", label="Search", scale=2)
            sort = gr.Radio(choices=["Newest First", "Oldest First"], value="Newest First", label="Sort")
            group = gr.Checkbox(label="Group IOCs by type (IP, URL, Hash)")

        results = gr.HTML()

        query.change(fn=render_summary_cards, inputs=[query, sort, group], outputs=results)
        sort.change(fn=render_summary_cards, inputs=[query, sort, group], outputs=results)
        group.change(fn=render_summary_cards, inputs=[query, sort, group], outputs=results)

        gr.Markdown("---")
        with gr.Accordion("🔁 Refresh Feeds + Re-Summarize", open=False):
            gr.Markdown("Will re-fetch feeds and re-run summaries using Ollama.")
            refresh_btn = gr.Button("🚀 Run Pipeline")
            refresh_btn.click(fn=refresh_pipeline, outputs=[])

        # ✅ Correctly trigger on app load
        app.load(fn=render_summary_cards, inputs=[query, sort, group], outputs=results)

    return app

if __name__ == "__main__":
    build_ui().launch()