"""
gemini_client.py
-----------------
Ye module Google Gemini API aur DeepSeek API (fallback ke tor par)
ke sath saara kaam handle karta hai:
- Clients configure karna (Gemini & DeepSeek API keys)
- Chat sessions banana
- Streaming response dena (automatic fallback ke sath)
- Errors ko gracefully handle karna
"""

import google.generativeai as genai
from openai import OpenAI

# Free tier mein available accha models
AVAILABLE_MODELS = [
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
]

DEFAULT_MODEL = "gemini-flash-latest"

# DeepSeek client setup ke liye default model
DEEPSEEK_MODEL = "deepseek-chat"


def configure_gemini(api_key: str) -> None:
    """Gemini API key set karta hai."""
    genai.configure(api_key=api_key)


def create_chat_session(system_prompt: str, history: list, model_name: str = DEFAULT_MODEL):
    """
    Naya Gemini chat session banata hai jisme system_prompt persona ke tor
    pe set hota hai, aur purani history restore hoti hai.
    """
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
    )
    chat = model.start_chat(history=history)
    return chat


def stream_reply(chat_session, user_message: str, gemini_api_key: str = None, deepseek_api_key: str = None, system_prompt: str = "", history: list = None):
    """
    Pehle Gemini se streaming response lene ki koshish karta hai.
    Agar quota khatam ho jaye (429) ya koi aur API limit aaye, 
    toh automatically DeepSeek API par switch karke response stream kar deta hai.
    """
    try:
        # Pehli koshish Gemini ke sath
        response = chat_session.send_message(user_message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as exc:
        error_text = str(exc)

        # Agar Gemini ka quota ya rate limit cross ho jaye, aur DeepSeek ki key di gayi ho
        if ("429" in error_text or "quota" in error_text.lower() or "ResourceExhausted" in error_text) and deepseek_api_key:
            yield "\n\n🔄 *Gemini ka quota/limit khatam ho gayi ustad, DeepSeek se connection switch ho raha hai...*\n\n"
            
            try:
                # DeepSeek OpenAI-compatible client initialize karna
                ds_client = OpenAI(
                    api_key=deepseek_api_key,
                    base_url="https://api.deepseek.com"
                )
                
                # History ko OpenAI format mein convert karna
                formatted_messages = [{"role": "system", "content": system_prompt}]
                if history:
                    for h in history:
                        role = "user" if h["role"] == "user" else "assistant"
                        parts = h.get("parts", [h.get("content", "")])
                        formatted_messages.append({"role": role, "content": parts[0]})
                
                # Current user message add karna
                formatted_messages.append({"role": "user", "content": user_message})
                
                # DeepSeek streaming call
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
                "\n\n⚠️ **Bhai Gemini API key ghalat hai!** Sidebar mein "
                "sahi Gemini API key daalo ya DeepSeek key configure karo."
            )
        else:
            yield f"\n\n⚠️ **Kuch gadbad ho gayi:** `{error_text}`\n\nDobara try karo."
