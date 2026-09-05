"""
CyberUstad AI
=============
Ek funny, roasting wala Cyber Security ustad jo Streamlit chat
interface ke zariye Red Team + Blue Team A-to-Z sikhata hai.

Run karne ka tareeqa:
    streamlit run app.py

Setup zaroori hai (README.md mein detail se hai):
    - GEMINI_API_KEY (secrets)
    - Google Login (secrets [auth] section) - taake log apni chats
      apne Google account se save kar sakein
    - (optional) SUPABASE_URL / SUPABASE_KEY - permanent storage
"""

import os
import sys

# Ensure current directory is in path for robust module importing
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import streamlit as st

from core.gemini_client import (
    DEFAULT_MODEL,
    configure_gemini,
    create_chat_session,
    stream_reply,
)
from core.persona import DIFFICULTY_LEVELS, WELCOME_MESSAGE, build_system_prompt
from core.storage import (
    delete_conversation,
    list_conversations,
    load_conversation,
    make_title,
    new_conversation_id,
    save_conversation,
)

# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="CyberUstad AI",
    page_icon="🕵️‍♂️",
    layout="centered",
)

st.title("🕵️‍♂️ CyberUstad AI")
st.caption("Red Team + Blue Team sikho... hasi hasi mein, roast khaate hue 😎🔥")

# ---------------------------------------------------------------------
# LOGIN GATE - Google se login karo (chats save hongi) ya Guest mode
# (chats save nahi hongi, sirf abhi ke liye).
# ---------------------------------------------------------------------
is_logged_in = getattr(st.user, "is_logged_in", False)

if not is_logged_in and not st.session_state.get("guest_mode"):
    st.info(
        "👋 Shuru karne se pehle ek choice karo:\n\n"
        "- **Google se login** karo taake tumhari chats hamesha ke liye "
        "save rahein aur kisi bhi device se wapis mil jayein.\n"
        "- Ya **Guest Mode** mein try karo - koi login nahi, lekin chat "
        "sirf isi session ke liye rahegi, save nahi hogi."
    )
    col1, col2 = st.columns(2)
    with col1:
        st.button("🔐 Continue with Google", use_container_width=True, type="primary", on_click=st.login)
    with col2:
        if st.button("👤 Guest Mode (bina save ke)", use_container_width=True):
            st.session_state.guest_mode = True
            st.rerun()
    st.stop()

if is_logged_in:
    user_id = st.user.email
    user_display = getattr(st.user, "name", None) or st.user.email
else:
    user_id = None  # Guest - koi persistent identity nahi
    user_display = "Guest"


# ---------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = new_conversation_id()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

if "settings_signature" not in st.session_state:
    st.session_state.settings_signature = None


def start_new_chat() -> None:
    st.session_state.conversation_id = new_conversation_id()
    st.session_state.messages = []
    st.session_state.gemini_history = []
    st.session_state.chat_session = None
    st.session_state.settings_signature = None


def load_chat(conversation_id: str) -> None:
    conv = load_conversation(user_id, conversation_id)
    st.session_state.conversation_id = conversation_id
    st.session_state.messages = conv.get("messages", [])
    st.session_state.gemini_history = conv.get("gemini_history", [])
    st.session_state.chat_session = None
    st.session_state.settings_signature = None


# ---------------------------------------------------------------------
# Sidebar - account, settings, saved chats
# ---------------------------------------------------------------------
with st.sidebar:
    st.title("🕵️‍♂️ CyberUstad")

    if is_logged_in:
        st.caption(f"👋 Salam, **{user_display}**")
        st.button("🚪 Logout", on_click=st.logout, use_container_width=True)
    else:
        st.caption("👤 Guest Mode - chats save nahi ho rahi")
        st.button("🔐 Login with Google", on_click=st.login, use_container_width=True)

    st.divider()

    if st.button("➕ Naya Chat", use_container_width=True, type="primary"):
        start_new_chat()
        st.rerun()

    st.divider()

    with st.expander("⚙️ Settings", expanded=False):
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

    if is_logged_in:
        st.caption("💬 Pichli Guftagu")
        conversations = list_conversations(user_id)
        if not conversations:
            st.caption("Abhi koi purani chat nahi hai.")
        else:
            for conv in conversations[:20]:
                is_active = conv["id"] == st.session_state.conversation_id
                col1, col2 = st.columns([5, 1])
                with col1:
                    label = ("👉 " if is_active else "") + conv["title"]
                    if st.button(label, key=f"open_{conv['id']}", use_container_width=True):
                        load_chat(conv["id"])
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{conv['id']}"):
                        delete_conversation(user_id, conv["id"])
                        if is_active:
                            start_new_chat()
                        st.rerun()
    else:
        st.caption("💬 Guest mode mein purani chats save/dikhai nahi hoti.")

    st.divider()
    st.caption(
        "Made with 😂 + ☕. Ye tool sirf educational purposes ke liye "
        "hai — authorized cybersecurity learning aur legal bug bounty "
        "practice ke liye."
    )


# ---------------------------------------------------------------------
# API key SIRF Streamlit secrets se aayegi.
# ---------------------------------------------------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "⚠️ **GEMINI_API_KEY set nahi hai!**\n\n"
        "Streamlit Cloud par: App ke 'Manage app' -> **Settings -> Secrets** "
        "mein jaake ye add karo:\n\n"
        "```toml\nGEMINI_API_KEY = \"your-key-here\"\n```"
    )
    st.stop()


# ---------------------------------------------------------------------
# Configure Gemini + (re)build chat session when needed
# ---------------------------------------------------------------------
settings_signature = (api_key, difficulty, focus, roast_level, st.session_state.conversation_id)

if st.session_state.settings_signature != settings_signature:
    try:
        configure_gemini(api_key)
        system_prompt = build_system_prompt(difficulty, roast_level, focus)
        st.session_state.chat_session = create_chat_session(
            system_prompt=system_prompt,
            history=st.session_state.gemini_history,
            model_name=DEFAULT_MODEL,
        )
        st.session_state.settings_signature = settings_signature
    except Exception as exc:  # noqa: BLE001
        st.error(f"API key ya model configure karne mein masla: {exc}")
        st.stop()


# ---------------------------------------------------------------------
# Show welcome message once (only for brand-new, empty chats)
# ---------------------------------------------------------------------
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        st.markdown(WELCOME_MESSAGE)


# ---------------------------------------------------------------------
# Render chat history
# ---------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "🕵️‍♂️" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if st.session_state.messages:
    transcript_lines = []
    for msg in st.session_state.messages:
        speaker = "CyberUstad" if msg["role"] == "assistant" else "Tum"
        transcript_lines.append(f"{speaker}: {msg['content']}\n")
    transcript = "\n".join(transcript_lines)
    st.download_button(
        "⬇️ Ye Chat Export Karo (.txt)",
        data=transcript,
        file_name=f"cyberustad-chat-{datetime.now().strftime('%Y%m%d-%H%M')}.txt",
        mime="text/plain",
        use_container_width=False,
    )


# ---------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------
user_input = st.chat_input("Apna sawal likho... (e.g. 'SQLi kya hoti hai?')")

if user_input:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.chat_session is None:
        st.error("Connection thori si atak gayi thi — dobara apna sawal bhej do.")
        st.session_state.settings_signature = None
        st.stop()

    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        full_reply = st.write_stream(
            stream_reply(st.session_state.chat_session, user_input)
        )

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.session_state.gemini_history.append({"role": "user", "parts": [user_input]})
    st.session_state.gemini_history.append({"role": "model", "parts": [full_reply]})

    # Sirf logged-in user ki chat save hoti hai. Guest mode mein
    # jaan boojh kar save nahi karte (jaisa user ne mangwaya).
    if is_logged_in:
        title = make_title(st.session_state.messages[0]["content"])
        save_conversation(
            user_id,
            st.session_state.conversation_id,
            title,
            st.session_state.messages,
            st.session_state.gemini_history,
        )
    st.rerun()
