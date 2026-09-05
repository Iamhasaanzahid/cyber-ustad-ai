"""
storage.py
----------
Chat history save/load karta hai, HAR USER KI ALAG SE (jo Google se
login karta hai uski chats sirf usko dikhti hain).

DO TAREEQAY (automatic switch):

1. AGAR Streamlit Secrets mein SUPABASE_URL aur SUPABASE_KEY set
   hain -> Supabase (asli, PERMANENT database) use hoga.
2. AGAR wo secrets nahi mile -> local JSON file use hoga (sirf
   local machine ke liye theek, Streamlit Cloud redeploy se reset
   ho jata hai).

Guest mode (bina login) mein history save NAHI hoti - sirf current
session ke liye chat chalti hai. Login karne walon ki history
unke Google account (email) se linked hoti hai.
"""

import json
import os
import uuid
from datetime import datetime, timezone

import requests
import streamlit as st

# -----------------------------------------------------------------
# Supabase config (agar available ho)
# -----------------------------------------------------------------
def _get_supabase_config():
    try:
        url = st.secrets["SUPABASE_URL"].rstrip("/")
        key = st.secrets["SUPABASE_KEY"]
        return url, key
    except Exception:
        return None, None


_SUPABASE_URL, _SUPABASE_KEY = _get_supabase_config()
USING_SUPABASE = bool(_SUPABASE_URL and _SUPABASE_KEY)

_TABLE = "conversations"


def _supabase_headers():
    return {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


# -----------------------------------------------------------------
# Local JSON fallback (jab Supabase configure nahi hai)
# Structure: { user_id: { conversation_id: {...} } }
# -----------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
STORAGE_FILE = os.path.join(DATA_DIR, "conversations.json")


def _ensure_local_storage() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _local_load_all() -> dict:
    _ensure_local_storage()
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _local_save_all(data: dict) -> None:
    _ensure_local_storage()
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------------------------------------------
# Public API - inhe app.py use karta hai. Har function ko user_id
# (Google login se aayi email) deni hoti hai, taake har user ki
# chats sirf usi ko dikhein.
# -----------------------------------------------------------------
def new_conversation_id() -> str:
    return str(uuid.uuid4())


def list_conversations(user_id: str) -> list:
    """[{id, title, updated_at}, ...] sabse naya pehle, SIRF is user ki."""
    if USING_SUPABASE:
        try:
            resp = requests.get(
                f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
                headers=_supabase_headers(),
                params={
                    "select": "id,title,updated_at",
                    "order": "updated_at.desc",
                    "user_id": f"eq.{user_id}",
                },
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []
    else:
        data = _local_load_all()
        user_convs = data.get(user_id, {})
        items = [
            {"id": cid, "title": conv.get("title", "Naya Chat"), "updated_at": conv.get("updated_at", "")}
            for cid, conv in user_convs.items()
        ]
        items.sort(key=lambda x: x["updated_at"], reverse=True)
        return items


def load_conversation(user_id: str, conversation_id: str) -> dict:
    empty = {"messages": [], "gemini_history": [], "title": "Naya Chat"}
    if USING_SUPABASE:
        try:
            resp = requests.get(
                f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
                headers=_supabase_headers(),
                params={"id": f"eq.{conversation_id}", "user_id": f"eq.{user_id}", "select": "*"},
                timeout=10,
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else empty
        except Exception:
            return empty
    else:
        data = _local_load_all()
        return data.get(user_id, {}).get(conversation_id, empty)


def save_conversation(user_id: str, conversation_id: str, title: str, messages: list, gemini_history: list) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    if USING_SUPABASE:
        try:
            payload = {
                "id": conversation_id,
                "user_id": user_id,
                "title": title,
                "messages": messages,
                "gemini_history": gemini_history,
                "updated_at": updated_at,
            }
            requests.post(
                f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
                headers={**_supabase_headers(), "Prefer": "resolution=merge-duplicates"},
                json=payload,
                timeout=10,
            )
        except Exception:
            pass
    else:
        data = _local_load_all()
        data.setdefault(user_id, {})[conversation_id] = {
            "title": title,
            "messages": messages,
            "gemini_history": gemini_history,
            "updated_at": updated_at,
        }
        _local_save_all(data)


def delete_conversation(user_id: str, conversation_id: str) -> None:
    if USING_SUPABASE:
        try:
            requests.delete(
                f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
                headers=_supabase_headers(),
                params={"id": f"eq.{conversation_id}", "user_id": f"eq.{user_id}"},
                timeout=10,
            )
        except Exception:
            pass
    else:
        data = _local_load_all()
        data.get(user_id, {}).pop(conversation_id, None)
        _local_save_all(data)


def make_title(first_user_message: str) -> str:
    text = first_user_message.strip().replace("\n", " ")
    if len(text) > 42:
        text = text[:42].rstrip() + "..."
    return text or "Naya Chat"
