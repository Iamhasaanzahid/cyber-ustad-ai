"""
gemini_client.py
-----------------
Ye module Google Gemini API ke sath saara kaam handle karta hai.
"""

import google.generativeai as genai

# Aapka pasandeeda 3.6-flash model sabse upar rakha hai
AVAILABLE_MODELS = [
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash-lite",
]

DEFAULT_MODEL = "gemini-3.6-flash"


def configure_gemini(api_key: str) -> None:
    """API key set karta hai."""
    genai.configure(api_key=api_key)


def create_chat_session(system_prompt: str, history: list, model_name: str = DEFAULT_MODEL):
    """Naya chat session banata hai purani history ke sath."""
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
    )
    chat = model.start_chat(history=history)
    return chat


def stream_reply(chat_session, user_message: str):
    """
    User ka message bhejta hai aur Gemini se streaming response deta hai.
    """
    try:
        response = chat_session.send_message(user_message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as exc:  
        error_text = str(exc)

        if "API_KEY_INVALID" in error_text or "API key not valid" in error_text:
            yield (
                "\n\n⚠️ **Bhai API key hi ghalat hai!** Sidebar mein "
                "sahi Gemini API key daalo."
            )
        elif "429" in error_text or "quota" in error_text.lower() or "ResourceExhausted" in error_text:
            yield (
                "\n\n⚠️ **Rate limit hit ho gayi ustad!** Google ki free tier limit ki wajah se "
                "connection thora busy hai. Ek sec ruko, agle message par ye khud theek ho jaye ga."
            )
        else:
            yield f"\n\n⚠️ **Kuch gadbad ho gayi:** `{error_text}`"
