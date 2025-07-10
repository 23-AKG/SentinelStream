import requests
import json

def summarize_article(text, title="Untitled", source_url="N/A", debug=False):
    if not text or not text.strip():
        return "⚠️ No content to summarize."

    api_url = "http://localhost:11434/api/chat"

    # Construct a focused and clean system prompt
    system_prompt = (
        f"You are a cybersecurity assistant.\n\n"
        f"TITLE: {title.strip()}\n"
        f"URL: {source_url.strip()}\n\n"
        "CONTENT:\n"
        f"{text.strip()}\n\n"
        "Summarize the article in exactly 3-4 concise bullet points. Each point should include one of the following:\n"
        "- Nature or type of threat\n"
        "- Affected targets or sectors\n"
        "- Known IOCs or techniques used\n\n"
        "Use markdown format. Start each point with '-'."
    )

    payload = {
        "model": "llama2",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text.strip()}
        ],
        "stream": True
    }

    try:
        response = requests.post(api_url, json=payload, stream=True, timeout=60)
        summary = ""

        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode("utf-8"))
                if debug:
                    print("🔹 Raw chunk:", data)
                summary += data.get("message", {}).get("content", "")
            except json.JSONDecodeError as e:
                if debug:
                    print(f"🔸 JSON decode warning: {e}")
                continue

        return summary.strip() if summary.strip() else "⚠️ No valid summary generated."

    except requests.exceptions.RequestException as e:
        return f"❌ API request failed: {e}"
