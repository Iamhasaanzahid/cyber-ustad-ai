"""
CyberUstad AI
=============
Ek funny, roasting wala Cyber Security ustad jo Streamlit chat
interface ke zariye Red Team + Blue Team A-to-Z sikhata hai.

Run karne ka tareeqa:
    streamlit run app.py

API key do tareeqon se de sakte ho:
    1. Sidebar mein directly paste kar do (sirf is session ke liye)
    2. .streamlit/secrets.toml mein GEMINI_API_KEY set kar do
       (permanent, GitHub pe push mat karna is file ko!)
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
# Session state defaults
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    # Ye display ke liye hai - [{"role": "user"/"assistant", "content": str}]
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    # Ye Gemini API ke format mein hai - [{"role": "user"/"model", "parts": [str]}]
    st.session_state.gemini_history = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

if "configured" not in st.session_state:
    st.session_state.configured = False


# ---------------------------------------------------------------------
# Sidebar - settings
# ---------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ CyberUstad Settings")

    difficulty = st.selectbox("📚 Tumhara Level", DIFFICULTY_LEVELS, index=0)

    focus = st.radio("🎯 Focus", ["Red Team", "Blue Team", "Both"], index=2)

    roast_level = st.slider(
        "🔥 Roast Intensity",
        min_value=1,
        max_value=3,
        value=2,
        help="1 = Halka mazaak, 3 = Full Ustad Mode (khoob tang karega)",
    )

    st.divider()

    if st.button("🗑️ Naya Chat Shuru Karo", use_container_width=True):
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.chat_session = None
        st.session_state.configured = False
        st.rerun()

    st.divider()
    st.caption(
        "Made with 😂 + ☕. Ye tool sirf educational purposes ke liye "
        "hai - authorized cybersecurity learning aur legal bug bounty "
        "practice ke liye."
    )


# ---------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------
st.title("🕵️‍♂️ CyberUstad AI")
st.caption("Red Team + Blue Team sikho... hasi hasi mein, roast khaate hue 😎🔥")

# API key SIRF Streamlit secrets se aayegi (sidebar input jaan boojh kar
# nahi rakha - taake key kabhi bhi chat screen par ya URL mein na aaye).
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "⚠️ **GEMINI_API_KEY set nahi hai!**\n\n"
        "Streamlit Cloud par: App ke 'Manage app' -> **Settings -> Secrets** "
        "mein jaake ye add karo:\n\n"
        "```toml\nGEMINI_API_KEY = \"your-key-here\"\n```\n\n"
        "Local par chalate ho to `.streamlit/secrets.toml` file mein daalo "
        "(dekho `.streamlit/secrets.toml.example`)."
    )
    st.stop()


# ---------------------------------------------------------------------
# Configure Gemini + (re)build chat session when settings change
# ---------------------------------------------------------------------
settings_signature = (api_key, difficulty, focus, roast_level)

if st.session_state.get("settings_signature") != settings_signature:
    try:
        configure_gemini(api_key)
        system_prompt = build_system_prompt(difficulty, roast_level, focus)
        st.session_state.chat_session = create_chat_session(
            system_prompt=system_prompt,
            history=st.session_state.gemini_history,
            model_name=DEFAULT_MODEL,
        )
        st.session_state.settings_signature = settings_signature
        st.session_state.configured = True
    except Exception as exc:  # noqa: BLE001
        st.error(f"API key ya model configure karne mein masla: {exc}")
        st.stop()


# ---------------------------------------------------------------------
# Show welcome message once
# ---------------------------------------------------------------------
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        st.markdown(WELCOME_MESSAGE)
    st.session_state.messages.append({"role": "assistant", "content": WELCOME_MESSAGE})


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
    # 1. User ka message dikhao aur save karo
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. Gemini se streaming reply lo
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        full_reply = st.write_stream(
            stream_reply(st.session_state.chat_session, user_input)
        )

    st.session_state.messages.append({"role": "assistant", "content": full_reply})

    # 3. Gemini history sync kar do (chat_session khud maintain karta hai,
    #    hum apna copy bhi rakhte hain taake session settings change hone
    #    par naya session banate waqt history restore ho sake)
    st.session_state.gemini_history.append({"role": "user", "parts": [user_input]})
    st.session_state.gemini_history.append({"role": "model", "parts": [full_reply]})
