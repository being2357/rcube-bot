"""
SQLite storage: found events + chat_ids subscribed to updates.
"""

import sqlite3
import hashlib
import os
from contextlib import contextmanager
from config import DB_PATH


def _make_id(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode("utf-8")).hexdigest()


@contextmanager
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                source TEXT,
                title TEXT,
                url TEXT,
                summary TEXT,
                found_at TEXT DEFAULT CURRENT_TIMESTAMP,
                sent_push INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                subscribed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                push_enabled INTEGER DEFAULT 1
            )
        """)


def add_event_if_new(source: str, title: str, url: str, summary: str = "") -> bool:
    """Insert event if not already present. Returns True if it was new."""
    event_id = _make_id(url, title)
    with get_conn() as conn:
        cur = conn.execute("SELECT 1 FROM events WHERE id = ?", (event_id,))
        if cur.fetchone():
            return False
        conn.execute(
            "INSERT INTO events (id, source, title, url, summary) VALUES (?, ?, ?, ?, ?)",
            (event_id, source, title, url, summary),
        )
        return True


def get_unsent_push_events():
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, source, title, url, summary FROM events WHERE sent_push = 0 ORDER BY found_at ASC"
        )
        return cur.fetchall()


def mark_push_sent(event_id: str):
    with get_conn() as conn:
        conn.execute("UPDATE events SET sent_push = 1 WHERE id = ?", (event_id,))


def get_events_last_n_hours(hours: int = 24):
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT source, title, url, summary FROM events
            WHERE found_at >= datetime('now', ?)
            ORDER BY found_at DESC
            """,
            (f"-{hours} hours",),
        )
        return cur.fetchall()


def add_subscriber(chat_id: int, username: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO subscribers (chat_id, username) VALUES (?, ?)",
            (chat_id, username),
        )


def remove_subscriber(chat_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))


def set_push_enabled(chat_id: int, enabled: bool):
    with get_conn() as conn:
        conn.execute(
            "UPDATE subscribers SET push_enabled = ? WHERE chat_id = ?",
            (1 if enabled else 0, chat_id),
        )


def get_all_subscribers(push_only: bool = False):
    with get_conn() as conn:
        if push_only:
            cur = conn.execute("SELECT chat_id FROM subscribers WHERE push_enabled = 1")
        else:
            cur = conn.execute("SELECT chat_id FROM subscribers")
        return [row[0] for row in cur.fetchall()]
