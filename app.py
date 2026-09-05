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
# Page config
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


# ---------------------------------------------------------------------
# Sidebar - Settings
# ---------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ CyberUstad Settings")

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
        st.rerun()

    st.caption("Made with 😂 + ☕. Educational purposes only.")


# ---------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------
st.title("🕵️‍♂️ CyberUstad AI")
st.caption("Red Team + Blue Team sikho... hasi hasi mein, roast khaate hue 😎🔥")


# ---------------------------------------------------------------------
# API Key Resolution
# ---------------------------------------------------------------------
active_api_key = None

if api_key_input and len(api_key_input.strip()) > 5:
    active_api_key = api_key_input.strip()

if not active_api_key:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            active_api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not active_api_key:
    st.error(
        "⚠️ **GEMINI_API_KEY nahi mili!**\n\n"
        "Baraye meharbani apni API key sidebar mein paste karein ya Streamlit secrets mein set karein."
    )
    st.stop()


# ---------------------------------------------------------------------
# Configure Gemini & Session Setup
# ---------------------------------------------------------------------
system_prompt = build_system_prompt(difficulty, roast_level, focus)
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
# Chat Input & Auto-Recovery Logic
# ---------------------------------------------------------------------
user_input = st.chat_input("Apna sawal likho... (Enter dabayein)")

if user_input:
    # 1. Show user message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. Ensure session exists
    if st.session_state.chat_session is None:
        try:
            configure_gemini(active_api_key)
            st.session_state.chat_session = create_chat_session(
                system_prompt=system_prompt,
                history=st.session_state.gemini_history,
                model_name=DEFAULT_MODEL,
            )
        except Exception:
            pass

    # 3. Stream reply with automatic fallback/recovery
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        try:
            full_reply = st.write_stream(
                stream_reply(st.session_state.chat_session, user_input)
            )
        except Exception:
            configure_gemini(active_api_key)
            st.session_state.chat_session = create_chat_session(
                system_prompt=system_prompt,
                history=st.session_state.gemini_history,
                model_name=DEFAULT_MODEL,
            )
            full_reply = st.write_stream(
                stream_reply(st.session_state.chat_session, user_input)
            )

    # 4. Save to history
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.session_state.gemini_history.append({"role": "user", "parts": [user_input]})
    st.session_state.gemini_history.append({"role": "model", "parts": [full_reply]})
