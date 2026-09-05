"""
gemini_client.py
-----------------
Ye module Google Gemini API aur DeepSeek API (fallback ke tor par)
ke sath saara kaam handle karta hai.
"""

import google.generativeai as genai
from openai import OpenAI

AVAILABLE_MODELS = [
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
]

DEFAULT_MODEL = "gemini-flash-latest"
DEEPSEEK_MODEL = "deepseek-chat"


def configure_gemini(api_key: str) -> None:
    """Gemini API key set karta hai."""
    genai.configure(api_key=api_key)


def create_chat_session(system_prompt: str, history: list, model_name: str = DEFAULT_MODEL):
    """Naya Gemini chat session banata hai."""
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
    )
    chat = model.start_chat(history=history)
    return chat


def stream_reply(chat_session, user_message: str, deepseek_api_key: str = None, system_prompt: str = "", history: list = None):
    """
    Pehle Gemini se response leta hai. Quota khatam hone par (429) 
    automatically DeepSeek API par switch ho jata hai.
    """
    try:
        response = chat_session.send_message(user_message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as exc:
        error_text = str(exc)

        if ("429" in error_text or "quota" in error_text.lower() or "ResourceExhausted" in error_text) and deepseek_api_key:
            yield "\n\n🔄 *Gemini ka quota khatam ho gaya ustad, DeepSeek par switch ho rahe hain...*\n\n"
            
            try:
                ds_client = OpenAI(
                    api_key=deepseek_api_key,
                    base_url="https://api.deepseek.com"
                )
                
                formatted_messages = [{"role": "system", "content": system_prompt}]
                if history:
                    for h in history:
                        role = "user" if h["role"] == "user" else "assistant"
                        parts = h.get("parts", [h.get("content", "")])
                        formatted_messages.append({"role": role, "content": parts[0]})
                
                formatted_messages.append({"role": "user", "content": user_message})
                
                stream = ds_client.chat.completions.create(
                    model=DEEPSEEK_MODEL,
                    messages=formatted_messages,
                    stream=True
                )
                
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                        
            except Exception as ds_exc:
                yield f"\n\n⚠️ **Dono APIs fail ho gayin!** Gemini error: `{error_text}` | DeepSeek error: `{ds_exc}`"
                
        elif "API_KEY_INVALID" in error_text or "API key not valid" in error_text:
            yield (
                "\n\n⚠️ **Bhai Gemini API key ghalat hai!** Sahi key enter karo."
            )
        else:
            yield f"\n\n⚠️ **Kuch gadbad ho gayi:** `{error_text}`\n\nDobara try karo."
