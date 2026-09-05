""""
groq_client.py
-----------------
Ye module Groq API ke sath ultra-fast streaming handle karta hai.
"""

from openai import OpenAI

# Yahan model name change kar diya hai taake 'model_not_found' error khatam ho jaye
DEFAULT_MODEL = "llama-3.1-8b-instant"

def create_groq_client(api_key: str):
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

def stream_groq_reply(client, system_prompt: str, history: list, user_message: str, model_name: str = DEFAULT_MODEL):
    try:
        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            role = "user" if h["role"] == "user" else "assistant"
            parts = h.get("parts", [h.get("content", "")])
            messages.append({"role": role, "content": parts[0]})
        
        messages.append({"role": "user", "content": user_message})

        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as exc:
        error_text = str(exc)
        if "invalid_api_key" in error_text.lower() or "unauthorized" in error_text.lower():
            yield "\n\n⚠️ **Bhai Groq API key ghalat hai!** Sahi key enter karo."
        else:
            yield f"\n\n⚠️ **Kuch gadbad ho gayi:** `{error_text}`"
