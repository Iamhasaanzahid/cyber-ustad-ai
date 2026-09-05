"""
CyberUstad AI
=============
Ek funny, roasting wala Cyber Security ustad jo Streamlit chat
interface ke zariye Red Team + Blue Team A-to-Z sikhata hai.
"""

import uuid
import streamlit as st

from core.gemini_client import (
    DEFAULT_MODEL,
    configure_gemini,
    create_chat_session,
    stream_reply,
)
from core.persona import DIFFICULTY_LEVELS, WELCOME_MESSAGE, build_system_prompt
from storage import load_chats, save_chats

# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="CyberUstad AI",
    page_icon="🕵️‍♂️",
    layout="centered",
)

# ---------------------------------------------------------------------
# Load Persistent Guest Chats
# ---------------------------------------------------------------------
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = load_chats()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

# ---------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None


# ---------------------------------------------------------------------
# Sidebar - settings & Guest Mode
# ---------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ CyberUstad Settings")

    # Guest Mode Toggle & History Management
    st.subheader("👤 Guest Session")
    guest_mode = st.toggle("Guest Mode (Save Chats)", value=True)

    if guest_mode and st.session_state.saved_chats:
        chat_titles = {cid: data.get("title", "New Chat") for cid, data in st.session_state.saved_chats.items()}
        selected_chat_id = st.selectbox(
            "📁 Purani Chats Select Karo",
            options=list(chat_titles.keys()),
            format_func=lambda x: chat_titles[x],
            index=list(chat_titles.keys()).index(st.session_state.current_chat_id) if st.session_state.current_chat_id in chat_titles else 0
        )
        
        # Agar user ne doosri chat select ki ho
        if selected_chat_id != st.session_state.current_chat_id:
            st.session_state.current_chat_id = selected_chat_id
            st.session_state.messages = st.session_state.saved_chats[selected_chat_id].get("messages", [])
            st.session_state.gemini_history = st.session_state.saved_chats[selected_chat_id].get("gemini_history", [])
            st.session_state.chat_session = None
            st.rerun()

    st.divider()

    # API Key input in sidebar (Optional override)
    api_key_input = st.text_input(
        "🔑 Gemini API Key (Optional)",
        type="password",
        placeholder="Agar secrets use nahi karne...",
        help="Yahan apni API key paste kar do agar session-based override chahiye."
    )

    st.divider()

    difficulty = st.selectbox("📚 Tumhara Level", DIFFICULTY_LEVELS, index=0)
    focus = st.radio("🎯 Focus", ["Red Team", "Blue Team", "Both"], index=2)
    roast_level = st.slider(
        "🔥 Roast Intensity",
        min_value=1,
        max_value=3,
        value=2,
        help="1 = Halka mazaak, 3 = Full Ustad Mode",
    )

    st.divider()

    if st.button("🗑️ Naya Chat Shuru Karo", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.chat_session = None
        st.session_state.settings_signature = None
        st.rerun()

    st.caption("Made with 😂 + ☕. Educational purposes only.")


# ---------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------
st.title("🕵️‍♂️ CyberUstad AI")
st.caption("Red Team + Blue Team sikho... hasi hasi mein, roast khaate hue 😎🔥")

# ---------------------------------------------------------------------
# Robust API Key Resolution (Fixes Secrets issue)
# ---------------------------------------------------------------------
api_key = None

# 1. Pehle check karo agar sidebar mein manual key di hai
if api_key_input and api_key_input.strip() and api_key_input != "AIzaSy...":
    api_key = api_key_input.strip()

# 2. Agar sidebar khali hai, toh Streamlit secrets se uthayo
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not api_key:
    st.error(
        "⚠️ **GEMINI_API_KEY set nahi hai!**\n\n"
        "Aapne Streamlit secrets mein key daali hai lekin wo load nahi ho rahi, "
        "ya toh sidebar mein paste kar do ya `secrets.toml` mein format check karo:\n\n"
        "```toml\nGEMINI_API_KEY = \"your_actual_key_here\"\n```"
    )
    st.stop()


# ---------------------------------------------------------------------
# Configure Gemini + (re)build chat session when settings change
# ---------------------------------------------------------------------
system_prompt = build_system_prompt(difficulty, roast_level, focus)
settings_signature = (api_key, difficulty, focus, roast_level)

if st.session_state.get("settings_signature") != settings_signature or st.session_state.chat_session is None:
    try:
        configure_gemini(api_key)
        st.session_state.chat_session = create_chat_session(
            system_prompt=system_prompt,
            history=st.session_state.gemini_history,
            model_name=DEFAULT_MODEL,
        )
        st.session_state.settings_signature = settings_signature
    except Exception as exc:  
        st.error(f"API key ya model configure karne mein masla: {exc}")
        st.stop()


# ---------------------------------------------------------------------
# Show welcome message once
# ---------------------------------------------------------------------
if not st.session_state.messages:
    welcome_content = WELCOME_MESSAGE
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        st.markdown(welcome_content)
    st.session_state.messages.append({"role": "assistant", "content": welcome_content})
    
    if guest_mode:
        st.session_state.saved_chats[st.session_state.current_chat_id] = {
            "title": "New Chat",
            "messages": st.session_state.messages,
            "gemini_history": st.session_state.gemini_history
        }
        save_chats(st.session_state.saved_chats)


# ---------------------------------------------------------------------
# Render chat history
# ---------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "🕵️‍♂️" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ---------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------
user_input = st.chat_input("Apna sawal likho... (e.g. 'SQLi kya hoti hai?')")

if user_input:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.chat_session is None:
        try:
            configure_gemini(api_key)
            st.session_state.chat_session = create_chat_session(
                system_prompt=system_prompt,
                history=st.session_state.gemini_history,
                model_name=DEFAULT_MODEL,
            )
        except Exception:
            st.error("Session expire ho gaya hai, dobara try karo.")
            st.stop()

    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        full_reply = st.write_stream(
            stream_reply(st.session_state.chat_session, user_input)
        )

    st.session_state.messages.append({"role": "assistant", "content": full_reply})

    st.session_state.gemini_history.append({"role": "user", "parts": [user_input]})
    st.session_state.gemini_history.append({"role": "model", "parts": [full_reply]})

    # Auto-save chat title using first user message if guest mode is on
    if guest_mode:
        chat_title = user_input[:25] + "..." if len(user_input) > 25 else user_input
        st.session_state.saved_chats[st.session_state.current_chat_id] = {
            "title": chat_title,
            "messages": st.session_state.messages,
            "gemini_history": st.session_state.gemini_history
        }
        save_chats(st.session_state.saved_chats)
