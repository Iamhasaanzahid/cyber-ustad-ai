"""
CyberUstad AI
=============
Ek funny, roasting wala Cyber Security ustad jo Streamlit chat
interface ke zariye Red Team + Blue Team A-to-Z sikhata hai.
"""

import streamlit as st

from core.gemini_client import (
    DEFAULT_MODEL,
    configure_gemini,
    create_chat_session,
    stream_reply,
)
from core.persona import DIFFICULTY_LEVELS, WELCOME_MESSAGE, build_system_prompt

# ---------------------------------------------------------------------
# Page config (Mobile friendly)
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="CyberUstad AI",
    page_icon="🕵️‍♂️",
    layout="centered",
)

# ---------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

if "last_api_key" not in st.session_state:
    st.session_state.last_api_key = None


# ---------------------------------------------------------------------
# Sidebar - Clean Settings (No Guest Mode)
# ---------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ CyberUstad Settings")

    # API Key Input (Sidebar option for direct user entry)
    api_key_input = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        help="Yahan apni API key paste karein ya secrets.toml use karein."
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
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.chat_session = None
        st.session_state.last_api_key = None
        st.rerun()

    st.caption("Made with 😂 + ☕. Educational purposes only.")


# ---------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------
st.title("🕵️‍♂️ CyberUstad AI")
st.caption("Red Team + Blue Team sikho... hasi hasi mein, roast khaate hue 😎🔥")


# ---------------------------------------------------------------------
# Robust API Key Detection (Fixes intermittent secret issues)
# ---------------------------------------------------------------------
active_api_key = None

# 1. Check sidebar input first
if api_key_input and len(api_key_input.strip()) > 5:
    active_api_key = api_key_input.strip()

# 2. Fallback to Streamlit Secrets if sidebar is empty
if not active_api_key:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            active_api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not active_api_key:
    st.error(
        "⚠️ **GEMINI_API_KEY nahi mili!**\n\n"
        "Baraye meharbani apni API key ya toh **sidebar mein paste karein**, "
        "ya phir Streamlit secrets (`secrets.toml`) mein is tarah set karein:\n\n"
        "```toml\nGEMINI_API_KEY = \"your-key-here\"\n```"
    )
    st.stop()


# ---------------------------------------------------------------------
# Configure Gemini & Chat Session Management
# ---------------------------------------------------------------------
system_prompt = build_system_prompt(difficulty, roast_level, focus)

# Agar API key ya settings change hui hain toh session fresh banega
settings_signature = (active_api_key, difficulty, focus, roast_level)

if st.session_state.get("settings_signature") != settings_signature or st.session_state.chat_session is None:
    try:
        configure_gemini(active_api_key)
        st.session_state.chat_session = create_chat_session(
            system_prompt=system_prompt,
            history=st.session_state.gemini_history,
            model_name=DEFAULT_MODEL,
        )
        st.session_state.settings_signature = settings_signature
    except Exception as exc:
        st.error(f"API key configure karne mein masla aa gaya: {exc}")
        st.stop()


# ---------------------------------------------------------------------
# Welcome Message
# ---------------------------------------------------------------------
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        st.markdown(WELCOME_MESSAGE)
    st.session_state.messages.append({"role": "assistant", "content": WELCOME_MESSAGE})


# ---------------------------------------------------------------------
# Render Chat History
# ---------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "🕵️‍♂️" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ---------------------------------------------------------------------
# Chat Input (Mobile & Enter Key Optimized)
# ---------------------------------------------------------------------
user_input = st.chat_input("Apna sawal likho... (Enter dabayein ya send karein)")

if user_input:
    # 1. Display and store user message immediately
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. Safety check for session
    if st.session_state.chat_session is None:
        try:
            configure_gemini(active_api_key)
            st.session_state.chat_session = create_chat_session(
                system_prompt=system_prompt,
                history=st.session_state.gemini_history,
                model_name=DEFAULT_MODEL,
            )
        except Exception:
            st.error("Session expire ho gaya hai, sidebar se 'Naya Chat Shuru Karo' dabayein.")
            st.stop()

    # 3. Stream reply from Gemini
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        full_reply = st.write_stream(
            stream_reply(st.session_state.chat_session, user_input)
        )

    # 4. Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.session_state.gemini_history.append({"role": "user", "parts": [user_input]})
    st.session_state.gemini_history.append({"role": "model", "parts": [full_reply]})
