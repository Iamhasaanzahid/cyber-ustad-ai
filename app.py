"""
CyberUstad AI (Groq Powered)
============================
Ek funny, roasting wala Cyber Security ustad jo Streamlit chat
interface ke zariye Red Team + Blue Team A-to-Z sikhata hai (Groq Edition).
"""

import streamlit as st

from core.groq_client import (
    DEFAULT_MODEL,
    create_groq_client,
    stream_groq_reply,
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

if "groq_history" not in st.session_state:
    st.session_state.groq_history = []


# ---------------------------------------------------------------------
# Sidebar - Settings
# ---------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ CyberUstad Settings")

    api_key_input = st.text_input(
        "🔑 Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Yahan apni Groq API key paste karein ya secrets.toml use karein."
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
        st.session_state.groq_history = []
        st.rerun()

    st.caption("Blazing fast AI via Groq ⚡")


# ---------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------
st.title("🕵️‍♂️ CyberUstad AI")
st.caption("Red Team + Blue Team sikho... lightning fast speed ke sath 😎🔥")


# ---------------------------------------------------------------------
# API Key Resolution
# ---------------------------------------------------------------------
active_api_key = None

if api_key_input and len(api_key_input.strip()) > 5:
    active_api_key = api_key_input.strip()

if not active_api_key:
    try:
        if "GROQ_API_KEY" in st.secrets:
            active_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

if not active_api_key:
    st.error(
        "⚠️ **GROQ_API_KEY nahi mili!**\n\n"
        "Baraye meharbani console.groq.com se free key lekar sidebar mein paste karein "
        "ya Streamlit secrets (`secrets.toml`) mein set karein:\n\n"
        "```toml\nGROQ_API_KEY = \"gsk_your_key_here\"\n```"
    )
    st.stop()


# ---------------------------------------------------------------------
# Initialize Groq Client & System Prompt
# ---------------------------------------------------------------------
system_prompt = build_system_prompt(difficulty, roast_level, focus)
groq_client = create_groq_client(active_api_key)


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
# Chat Input & Streaming Reply
# ---------------------------------------------------------------------
user_input = st.chat_input("Apna sawal likho... (Enter dabayein)")

if user_input:
    # 1. Show user message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. Stream reply from Groq
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        full_reply = st.write_stream(
            stream_groq_reply(
                client=groq_client,
                system_prompt=system_prompt,
                history=st.session_state.groq_history,
                user_message=user_input,
                model_name=DEFAULT_MODEL
            )
        )

    # 3. Save to history
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.session_state.groq_history.append({"role": "user", "parts": [user_input]})
    st.session_state.groq_history.append({"role": "model", "parts": [full_reply]})
