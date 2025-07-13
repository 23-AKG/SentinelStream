import json
import os
import gradio as gr
from datetime import datetime
import re
import tempfile

SUMMARY_PATH = "data/summaries.json"
IOC_INDEX_PATH = "data/ioc_index.json"
ITEMS_PER_PAGE = 10

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
    
def generate_pagination_html(current_page, total_pages, display_range=5):
    html = "<div style='text-align:center; margin: 10px 0;'>"
    start = max(0, current_page - display_range // 2)
    end = min(total_pages, start + display_range)

    if start > 0:
        html += f"<button onclick='document.querySelector(\"#page_state input\").value={current_page - 1}; document.querySelector(\"#update_cards\").click();'>&laquo;</button> "

    for i in range(start, end):
        if i == current_page:
            html += f"<button disabled style='font-weight:bold; background: #4faaff; color: black; margin:2px; padding: 4px 8px; border-radius: 4px;'>{i+1}</button>"
        else:
            html += f"<button onclick='document.querySelector(\"#page_state input\").value={i}; document.querySelector(\"#update_cards\").click();' style='margin:2px; padding: 4px 8px; border-radius: 4px;'>{i+1}</button>"

    if end < total_pages:
        html += f" <button onclick='document.querySelector(\"#page_state input\").value={current_page + 1}; document.querySelector(\"#update_cards\").click();'>&raquo;</button>"

    html += "</div>"
    return html



def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def is_valid_summary(text: str) -> bool:
    if not text.strip():
        return False
    return not (
        "skipped llm summarization" in text.lower()
        or "no valid summary" in text.lower()
        or text.strip().startswith("⚠️ Skipped")
    )

def load_summaries():
    all_summaries = load_json(SUMMARY_PATH)
    return {
        url: entry
        for url, entry in all_summaries.items()
        if is_valid_summary(entry.get("summary", ""))
    }

def load_ioc_index():
    return load_json(IOC_INDEX_PATH)

def export_iocs(title, url, ipv4, urls, hashes):
    lines = [f"Title: {title}", f"Link: {url}", "", "IOCs:"]
    if ipv4: lines += ["\nIPv4:"] + ipv4
    if urls: lines += ["\nURLs:"] + urls
    if hashes: lines += ["\nHashes:"] + hashes

    safe_title = re.sub(r"[^a-zA-Z0-9]", "_", title)[:30]
    temp_path = os.path.join(tempfile.gettempdir(), f"ioc_dump_{safe_title}.txt")
    with open(temp_path, "w") as f:
        f.write("\n".join(lines))
    return temp_path

def download_ioc_file(trigger_title):
    print(f"[DEBUG] Trigger title from dropdown: {trigger_title}")
    summaries = load_summaries()
    ioc_index = load_ioc_index()
    for url, entry in summaries.items():
        if entry["title"] == trigger_title:
            iocs = ioc_index.get(url, {})
            print(f"[DEBUG] Found entry. Exporting IOCs for: {entry['title']}")
            path = export_iocs(entry["title"], url, iocs.get("ipv4", []), iocs.get("url", []), iocs.get("hash", []))
            if os.path.exists(path):
                print(f"[INFO] File created at: {path}")
                return path
            else:
                print("[ERROR] File export failed or path missing.")
                return None
    print(f"[WARN] No matching title found for: {trigger_title}")
    return None


def get_source_tag(link):
    return "GitHub" if "github" in link else "RSS"

def generate_cards(summaries, ioc_index, query, sort_order, page):
    if query is None:
        query = ""
    if sort_order is None:
        sort_order = "Newest First"
    filtered = []
    for url, entry in summaries.items():
        combined_text = (entry["title"] + entry["summary"]).lower()
        if query.lower() in combined_text:
            filtered.append((url, entry))

    reverse = sort_order == "Newest First"
    filtered.sort(key=lambda x: x[1]["llm_meta"]["generated_on"], reverse=reverse)

    total_pages = max(1, (len(filtered) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    paged = filtered[page * ITEMS_PER_PAGE:(page + 1) * ITEMS_PER_PAGE]

    cards = ""
    for url, entry in paged:
        title = entry["title"]
        summary = entry["summary"]
        source = get_source_tag(entry["link"])
        date = entry["llm_meta"]["generated_on"].split("T")[0]

        iocs = ioc_index.get(url, {})
        ipv4, urls, hashes = iocs.get("ipv4", []), iocs.get("url", []), iocs.get("hash", [])
        total_iocs = len(ipv4) + len(urls) + len(hashes)

        if total_iocs > 0:
            ioc_details = ""
            if ipv4:
                ioc_details += f"<details><summary>IPv4 ({len(ipv4)})</summary><ul>" + "".join(f"<li>{ip}</li>" for ip in ipv4) + "</ul></details>"
            if urls:
                ioc_details += f"<details><summary>URL ({len(urls)})</summary><ul>" + "".join(f"<li>{u}</li>" for u in urls) + "</ul></details>"
            if hashes:
                ioc_details += f"<details><summary>Hash ({len(hashes)})</summary><ul>" + "".join(f"<li>{h}</li>" for h in hashes) + "</ul></details>"
            ioc_display = f"""
                <div style='margin-top: 8px; color: limegreen;'>✅ {total_iocs} IOCs Found</div>
                <details><summary>🔍 View IOCs</summary>{ioc_details}</details>
                <div style='margin-top: 6px; color: orange;'>Select this title below to download</div>
            """
        else:
            ioc_display = ""

        card = f"""
        <div style='padding: 14px; border-radius: 12px; background: #1f1f1f; margin-bottom: 16px; box-shadow: 0 0 6px rgba(0,0,0,0.4);'>
            <h3>{title}</h3>
            <div style='font-size: 0.9em; color: gray;'>{date} • <span style='color: orange;'>{source}</span></div>
            <div style='margin-top: 1em; white-space: pre-wrap;'>{summary}</div>

            {ioc_display}
            <div style='margin-top: 10px;'><a href="{url}" target="_blank" style='color: #4faaff;'>🔗 View Original</a></div>
        </div>
        """
        cards += card

    pagination = generate_pagination_html(page, total_pages)
    return cards, pagination, page

def get_titles_with_iocs_on_page(summaries, ioc_index, query, sort_order, page):
    if query is None:
        query = ""
    if sort_order is None:
        sort_order = "Newest First"

    filtered = []
    for url, entry in summaries.items():
        combined_text = (entry["title"] + entry["summary"]).lower()
        if query.lower() in combined_text:
            filtered.append((url, entry))

    reverse = sort_order == "Newest First"
    filtered.sort(key=lambda x: x[1]["llm_meta"]["generated_on"], reverse=reverse)

    total_pages = max(1, (len(filtered) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    paged = filtered[page * ITEMS_PER_PAGE:(page + 1) * ITEMS_PER_PAGE]

    return [entry["title"] for url, entry in paged if ioc_index.get(url)]


def update_cards(query, sort_order, page):
    summaries = load_summaries()
    ioc_index = load_ioc_index()
    cards_html, pagination_html, new_page = generate_cards(summaries, ioc_index, query, sort_order, page)
    dropdown_titles = get_titles_with_iocs_on_page(summaries, ioc_index, query, sort_order, new_page)
    return cards_html, pagination_html, new_page, gr.update(choices=dropdown_titles)


def list_articles_with_iocs():
    summaries = load_summaries()
    ioc_index = load_ioc_index()
    return [entry["title"] for url, entry in summaries.items() if ioc_index.get(url)]

def refresh_pipeline():
    os.system("python3 feeds/fetcher.py && python3 feeds/github_fetcher.py && python3 generate_summaries.py")
    return "✅ Pipeline re-run complete."


def build_ui():
    with gr.Blocks() as app:
        gr.Markdown("## 🛡️ SentinelStream Dashboard")
        gr.Markdown("Real-time AI summaries and threat intelligence viewer")

        # 🔹 Feed Overview Tab
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

            for button, name in zip([b1, b2, b3, b4, b5, b6, b7, b8], FEED_FILES.keys()):
                hidden_input = gr.Textbox(value=name, visible=False)
                button.click(load_feed_content_partial, inputs=[hidden_input], outputs=feed_output)
                button.click(fn=lambda x: x, inputs=[hidden_input], outputs=more_input)

            more_button.click(load_feed_full, inputs=more_input, outputs=full_output)

        # 🔹 Full Feed View Tab
        with gr.Tab("📖 Full Feed View"):
            gr.Markdown("Below is the full feed content of the last feature you selected:")
            full_view = gr.Markdown()
            more_button.click(load_feed_full, inputs=more_input, outputs=full_view)

        # 🔹 IOC Search Tab
        with gr.Tab("🔍 Search IOC in Feed"):
            gr.Markdown("Check if your IP, URL, hash, or domain is malicious")
            selected_feed = gr.Dropdown(choices=list(FEED_FILES.keys()), label="Select Feed")
            user_input = gr.Textbox(label="Enter IOC to search (e.g. IP, hash, URL)")
            search_btn = gr.Button("Check Now")
            result = gr.Markdown()
            search_btn.click(check_if_malicious, inputs=[selected_feed, user_input], outputs=result)

        # 🔹 Summary Cards Tab
        with gr.Tab("🧠 AI Summary Cards"):
            with gr.Row():
                query = gr.Textbox(label="Search", placeholder="Keyword, threat, actor", scale=2)
                sort = gr.Radio(choices=["Newest First", "Oldest First"], value="Newest First")
            
            html_display = gr.HTML()
            pagination_html = gr.HTML()
            
            page_state = gr.Number(value=0, visible=False)
            update_btn = gr.Button(visible=False, elem_id="update_cards")

            # Dropdown and Download
            with gr.Row():
                refresh_iocs_btn = gr.Button("🔄 Refresh Article List")
                ioc_selector = gr.Dropdown(label="Select IOC Article", choices=[], value=None)

            download_btn = gr.Button("📎 Download Selected IOC File")
            download_file = gr.File(label="Your Download", interactive=False, visible=False)

            # Summary card logic
            def handle_download(trigger_title):
                print(f"[DEBUG] Trigger title from dropdown: {trigger_title}")
                path = download_ioc_file(trigger_title)
                if path and os.path.exists(path):
                    print(f"[INFO] File created at: {path}")
                    return gr.update(value=path, visible=True)
                return gr.update(visible=False)

            def hide_file():
                return gr.update(visible=False)

            query.change(update_cards, inputs=[query, sort, page_state], outputs=[html_display, pagination_html, page_state, ioc_selector])
            sort.change(update_cards, inputs=[query, sort, page_state], outputs=[html_display, pagination_html, page_state, ioc_selector])
            update_btn.click(update_cards, inputs=[query, sort, page_state], outputs=[html_display, pagination_html, page_state, ioc_selector])
            app.load(update_cards, inputs=[query, sort, page_state], outputs=[html_display, pagination_html, page_state, ioc_selector])

            prev_btn = gr.Button("⬅️ Prev")
            next_btn = gr.Button("Next ➡️")
            prev_btn.click(lambda q, s, p: update_cards(q, s, p - 1), inputs=[query, sort, page_state], outputs=[html_display, pagination_html, page_state, ioc_selector])
            next_btn.click(lambda q, s, p: update_cards(q, s, p + 1), inputs=[query, sort, page_state], outputs=[html_display, pagination_html, page_state, ioc_selector])

            gr.Markdown("---")
            gr.Markdown("### 📥 Download IOCs from a specific article")

            refresh_iocs_btn.click(fn=list_articles_with_iocs, outputs=ioc_selector)
            download_btn.click(hide_file, outputs=download_file, show_progress=False)
            download_btn.click(handle_download, inputs=ioc_selector, outputs=download_file)


        with gr.Tab("📝 Analyze My Article"):
            gr.Markdown("Paste a link to any threat article below to extract title, summary, and IOCs.")

            user_article_url = gr.Textbox(label="Article URL", placeholder="https://...")

            analyze_btn = gr.Button("🔍 Analyze Link")

            output_summary = gr.Markdown()
            output_iocs = gr.HTML()
            download_user_ioc = gr.File(label="Download IOCs", interactive=False, visible=False)

            def analyze_link(url):
                from processors.ioc_extractor import extract_iocs
                from processors.gemini_summarizer import summarize_with_gemini
                import requests, re, tempfile
                from bs4 import BeautifulSoup
                from bs4 import XMLParsedAsHTMLWarning
                import warnings
                warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

                try:
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.text, "html.parser")
                    title = soup.title.string.strip() if soup.title else "Untitled"
                    paragraphs = soup.find_all('p')
                    content = "\n".join(p.get_text() for p in paragraphs)
                    if not content.strip():
                        return "❌ No readable content found", "", ""
                except Exception as e:
                    return f"❌ Failed to fetch article: {e}", "", ""

                summary = summarize_with_gemini(content, url)
                iocs = extract_iocs(content)

                details_html = ""
                if iocs["ipv4"]:
                    details_html += f"<details><summary>IPv4 ({len(iocs['ipv4'])})</summary><ul>" + "".join(f"<li>{ip}</li>" for ip in iocs["ipv4"]) + "</ul></details>"
                if iocs["url"]:
                    details_html += f"<details><summary>URL ({len(iocs['url'])})</summary><ul>" + "".join(f"<li>{u}</li>" for u in iocs["url"]) + "</ul></details>"
                if iocs["hash"]:
                    details_html += f"<details><summary>Hash ({len(iocs['hash'])})</summary><ul>" + "".join(f"<li>{h}</li>" for h in iocs["hash"]) + "</ul></details>"

                # Save IOCs to file
                safe_title = re.sub(r"[^a-zA-Z0-9]", "_", title)[:30]
                temp_path = os.path.join(tempfile.gettempdir(), f"user_iocs_{safe_title}.txt")

                try:
                    with open(temp_path, "w") as f:
                        f.write(f"Title: {title}\nLink: {url}\n\nSummary:\n{summary}\n\nIOCs:\n")
                        for typ, items in iocs.items():
                            if items:
                                f.write(f"\n{typ.upper()}:\n" + "\n".join(items))
                except Exception as e:
                    print(f"❌ Failed to write IOCs file: {e}")
                    temp_path = ""

                return summary, details_html, temp_path

            analyze_btn.click(analyze_link, inputs=[user_article_url], outputs=[output_summary, output_iocs, download_user_ioc])
            download_user_ioc.change(lambda x: gr.update(visible=True), inputs=download_user_ioc, outputs=download_user_ioc)
        # 🔹 Pipeline Refresh Section
        with gr.Accordion("🔁 Refresh Feeds + Re-Summarize", open=False):
            gr.Markdown("Will re-fetch feeds and re-run summaries using Ollama.")
            refresh_btn = gr.Button("🚀 Run Pipeline")
            refresh_btn.click(fn=refresh_pipeline, outputs=[])
    return app


if __name__ == "__main__":
    build_ui().launch()