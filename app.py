"""
CyberUstad AI
=============
Ek funny, roasting wala Cyber Security ustad jo Streamlit chat
interface ke zariye Red Team + Blue Team A-to-Z sikhata hai.
"""

import uuid
from datetime import datetime
import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------------------
# Constants & Persona Settings
# ---------------------------------------------------------------------
DEFAULT_MODEL = "gemini-1.5-flash"

DIFFICULTY_LEVELS = [
    "Beginner (Noob - Zero Knowledge)",
    "Intermediate (Script Kiddie - Thora Bohot Pata Hai)",
    "Advanced (Hacker - Pro Level)"
]

WELCOME_MESSAGE = (
    "Salam dost! Main hoon **CyberUstad**. Red Team ho ya Blue Team, "
    "sab seekha dunga — par pehle achhi tarah roast khaane ke liye tayyar ho jao! 😎🔥\n\n"
    "Batao, aaj kya seekhna hai? Koi bug bounty ka sawal ya SOC log analysis?"
)

def build_system_prompt(difficulty: str, roast_level: int, focus: str) -> str:
    return f"""You are CyberUstad AI, an expert, witty, and humorous cybersecurity mentor who teaches Red Team and Blue Team operations. 
Your tone mixes Roman Urdu and English with heavy roasting, desi humor, and deep technical accuracy.
Current Settings:
- Difficulty Level: {difficulty}
- Roast Intensity: {roast_level} (Scale 1 to 3, where 3 is full Ustad mode with maximum roasting)
- Focus Area: {focus}

Always guide the user step-by-step, explain exploits or defense mechanisms clearly, maintain a roasting persona, and emphasize legal, ethical, and authorized security practices.
"""

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
# LOGIN GATE
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

user_id = st.user.email if is_logged_in else None
user_display = getattr(st.user, "name", None) or st.user.email if is_logged_in else "Guest"

# ---------------------------------------------------------------------
# Storage Helpers (In-Session / Dictionary Based)
# ---------------------------------------------------------------------
def new_conversation_id() -> str:
    return str(uuid.uuid4())

def make_title(first_message: str) -> str:
    clean = first_message.strip().replace("\n", " ")
    return clean[:30] + ("..." if len(clean) > 30 else "")

def list_conversations(uid: str):
    if "db_conversations" not in st.session_state:
        st.session_state.db_conversations = {}
    if uid not in st.session_state.db_conversations:
        st.session_state.db_conversations[uid] = {}
    return [{"id": cid, "title": data.get("title", "Chat")} for cid, data in st.session_state.db_conversations[uid].items()]

def load_conversation(uid: str, cid: str):
    if "db_conversations" in st.session_state and uid in st.session_state.db_conversations:
        return st.session_state.db_conversations[uid].get(cid, {})
    return {}

def save_conversation(uid: str, cid: str, title: str, messages):
    if "db_conversations" not in st.session_state:
        st.session_state.db_conversations = {}
    if uid not in st.session_state.db_conversations:
        st.session_state.db_conversations[uid] = {}
    st.session_state.db_conversations[uid][cid] = {
        "title": title,
        "messages": messages,
    }

def delete_conversation(uid: str, cid: str):
    if "db_conversations" in st.session_state and uid in st.session_state.db_conversations:
        if cid in st.session_state.db_conversations[uid]:
            del st.session_state.db_conversations[uid][cid]

# ---------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = new_conversation_id()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "settings_signature" not in st.session_state:
    st.session_state.settings_signature = None

def start_new_chat() -> None:
    st.session_state.conversation_id = new_conversation_id()
    st.session_state.messages = []
    st.session_state.chat_session = None
    st.session_state.settings_signature = None

def load_chat(cid: str) -> None:
    conv = load_conversation(user_id, cid)
    st.session_state.conversation_id = cid
    st.session_state.messages = conv.get("messages", [])
    st.session_state.chat_session = None
    st.session_state.settings_signature = None

# ---------------------------------------------------------------------
# Sidebar
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

# ---------------------------------------------------------------------
# API Key Check
# ---------------------------------------------------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ **GEMINI_API_KEY set nahi hai!** Secrets mein add karo.")
    st.stop()

# ---------------------------------------------------------------------
# Configure Gemini Session & Rebuild history if needed
# ---------------------------------------------------------------------
settings_signature = (api_key, difficulty, focus, roast_level, st.session_state.conversation_id)

if st.session_state.settings_signature != settings_signature or st.session_state.chat_session is None:
    try:
        genai.configure(api_key=api_key)
        system_prompt = build_system_prompt(difficulty, roast_level, focus)
        model = genai.GenerativeModel(model_name=DEFAULT_MODEL, system_instruction=system_prompt)
        
        # Rebuild native chat session history from st.session_state.messages
        gemini_history = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
            
        st.session_state.chat_session = model.start_chat(history=gemini_history)
        st.session_state.settings_signature = settings_signature
    except Exception as exc:
        st.error(f"API key ya model configure karne mein masla: {exc}")
        st.stop()

if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        st.markdown(WELCOME_MESSAGE)

for msg in st.session_state.messages:
    avatar = "🕵️‍♂️" if msg["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

user_input = st.chat_input("Apna sawal likho... (e.g. 'SQLi kya hoti hai?')")

if user_input:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="🕵️‍♂️"):
        response = st.session_state.chat_session.send_message(user_input, stream=True)
        def generate():
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        full_reply = st.write_stream(generate())

    st.session_state.messages.append({"role": "assistant", "content": full_reply})

    if is_logged_in:
        title = make_title(st.session_state.messages[0]["content"])
        save_conversation(user_id, st.session_state.conversation_id, title, st.session_state.messages)
    st.rerun()
