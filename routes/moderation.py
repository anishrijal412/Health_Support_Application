from routes.mod_professor import professor_moderation
from routes.mod_gemini import gemini_moderation

# Change this to "professor" or "gemini"
MODERATION_SOURCE = "gemini"        # default

def normalize_response(result):
    if not isinstance(result, tuple):
        return True, "Content allowed.", None
    if len(result) == 2:
        return result[0], result[1], None
    return result[0], result[1], result[2]

def is_safe_content_ai(text):
    if MODERATION_SOURCE == "gemini":
        print("[Moderator] Using Gemini AI")
        return normalize_response(gemini_moderation(text))

    print("[Moderator] Using Professor AI")
    return normalize_response(professor_moderation(text))
