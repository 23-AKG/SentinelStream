import requests

# 🔐 Paste your Gemini API key here directly
GEMINI_API_KEY = "AIzaSyBna_i1nBdM6RPDvMcf5zpgCMJAWB8mdFM"  # <--- Replace this!

def summarize_with_gemini(article_text, article_url=""):
    prompt = f"""
Summarize the following threat intelligence article in 3-5 bullet points. 
Focus on key IOCs, malware, threat actors, campaigns, or techniques involved.

URL: {article_url}

Article:
\"\"\"
{article_text}
\"\"\"
"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        headers=headers,
        json=body
    )

    try:
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"❌ Gemini API error: {e}"
