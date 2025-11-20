import requests

API_URL = "http://cmsai:8000/generate/"

def professor_moderation(text):
    """Call Professor's campus moderation API."""
    try:
        response = requests.post(API_URL, json={"prompt": text}, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"[Professor AI] Moderation response:", data)
    except Exception as e:
        print(f"[Professor AI] Error:", e)
        return True, "Professor AI unavailable (fallback allowed)."

    safety = data.get("safety", "safe").lower()
    categories = [c.lower() for c in data.get("categories", [])]

    flagged_keywords = ["self-harm","self harm","suicide","violence","harm"]
    matched = [c for c in categories if any(k in c for k in flagged_keywords)]

    if safety == "unsafe":
        detail = "Professor AI flagged content as unsafe."
        if matched:
            detail += f" Categories: {', '.join(matched)}."
        return False, detail

    if matched:
        return False, f"Professor AI detected harmful content: {', '.join(matched)}"

    return True, "Professor AI cleared the content as safe."
