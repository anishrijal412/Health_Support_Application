import os
import requests
from flask import Blueprint, jsonify

api_test = Blueprint("api_test", __name__)

@api_test.route("/test-gemini")
def test_gemini():
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")

    if not GEMINI_KEY:
        return jsonify({"error": "Gemini API key not set."}), 400

    # Use the supported model from your list
    model = "models/gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={GEMINI_KEY}"

    data = {
        "contents": [{
            "parts": [{"text": "Say hello in one friendly sentence."}]
        }]
    }

    try:
        response = requests.post(url, json=data)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
