"""
gemini_client.py
-----------------
Ye module Google Gemini API ke sath saara kaam handle karta hai:
- Client configure karna (API key)
- Chat session banana (with system instruction)
- Streaming response dena taake chat msg jaisa real-time feel aaye
- Errors ko gracefully handle karna (rate limit, invalid key, etc.)
"""

import google.generativeai as genai


# Free tier mein available accha models (Sept 2026 tak jo available thay).
# Agar Google naya model laye to yahan add kar dena.
AVAILABLE_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

DEFAULT_MODEL = "gemini-2.0-flash"


def configure_gemini(api_key: str) -> None:
    """API key set karta hai. Ye call karne se pehle koi aur
    genai function call mat karna."""
    genai.configure(api_key=api_key)


def create_chat_session(system_prompt: str, history: list, model_name: str = DEFAULT_MODEL):
    """
    Naya chat session banata hai jisme system_prompt persona ke tor
    pe set hota hai, aur purani history (agar hai) restore hoti hai.

    history format: list of {"role": "user"/"model", "parts": [text]}
    """
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
    )
    chat = model.start_chat(history=history)
    return chat


def stream_reply(chat_session, user_message: str):
    """
    User ka message bhejta hai aur Gemini se streaming response
    generator ke tor pe return karta hai (Streamlit ke st.write_stream
    ke sath direct use ho sakta hai).

    Kisi bhi API error ko yahan catch karke ek readable Urdu/English
    error message ke tor pe yield kar dete hain, taake app crash na ho.
    """
    try:
        response = chat_session.send_message(user_message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as exc:  # noqa: BLE001 - hum har error ko user ko dikhana chahte hain
        error_text = str(exc)

        if "API_KEY_INVALID" in error_text or "API key not valid" in error_text:
            yield (
                "\n\n⚠️ **Bhai API key hi ghalat hai!** Sidebar mein "
                "sahi Gemini API key daalo (AI Studio se free milti hai). "
                "Filhaal main tumhein roast bhi nahi kar sakta kyunke "
                "mujhe khud connection nahi mil raha 😅"
            )
        elif "429" in error_text or "quota" in error_text.lower():
            yield (
                "\n\n⚠️ **Thoda ruk jao ustad!** Free tier ka rate "
                "limit/quota khatam ho gaya lagta hai. Thori dair mein "
                "phir try karo, ya API key change kar lo."
            )
        else:
            yield f"\n\n⚠️ **Kuch gadbad ho gayi:** `{error_text}`\n\nDobara try karo."
