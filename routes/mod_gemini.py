import os
import json
import re
import requests

def extract_json(text):
    """
    Extracts JSON object from Gemini output.
    Removes backticks, ```json, and any extra text.
    """
    if not text:
        return None

    # 1. Remove markdown code block wrappers
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    cleaned = cleaned.replace("```", "").strip()

    # 2. Extract JSON between { }
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return match.group(0)

    return None


def gemini_moderation(text: str):
    """Moderate content using Gemini 2.5 Flash."""

    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_KEY:
        return False, "Gemini API key missing."

    model = "models/gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={GEMINI_KEY}"

    prompt = (
        "Moderate the following forum text.\n"
        "Return ONLY a JSON object like:\n"
        "{ \"safe\": true/false, \"reason\": \"text\", \"categories\": [] }\n\n"
        f"TEXT: {text}"
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload)
        full = response.json()

        print("\n--- GEMINI RAW RESPONSE ---")
        print(full)
        print("--- END ---\n")

        # Extract the model output text
        raw_text = (
            full.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
        )

        # Clean & extract JSON
        json_str = extract_json(raw_text)
        if not json_str:
            raise ValueError("Could not extract JSON from Gemini response")

        ai = json.loads(json_str)

        is_safe = ai.get("safe", True)
        reason = ai.get("reason", "No explanation")

        return is_safe, f"Gemini: {reason}"

    except Exception as e:
        print("[Gemini Error]", e)
        return True, "Gemini unavailable (fallback allowed)."
