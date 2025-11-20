from routes.mod_professor import professor_moderation
from routes.mod_gemini import gemini_moderation

# Change this to "professor" or "gemini"
MODERATION_SOURCE = "gemini"        # default

def is_safe_content_ai(text):
    if MODERATION_SOURCE == "gemini":
        print("[Moderator] Using Gemini AI")
        return gemini_moderation(text)

    print("[Moderator] Using Professor AI")
    return professor_moderation(text)
