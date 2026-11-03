"""Persistence: links in SQLite, hit counters in Redis."""
import sqlite3

import redis

_db = sqlite3.connect("links.db", check_same_thread=False)
_db.execute("CREATE TABLE IF NOT EXISTS links (code TEXT PRIMARY KEY, url TEXT)")
_hits = redis.Redis()


def save(code: str, url: str) -> None:
    _db.execute("INSERT INTO links VALUES (?, ?)", (code, url))
    _db.commit()


def load(code: str) -> str | None:
    row = _db.execute("SELECT url FROM links WHERE code = ?", (code,)).fetchone()
    return row[0] if row else None


def count_hit(code: str) -> None:
    _hits.incr(f"hits:{code}")
