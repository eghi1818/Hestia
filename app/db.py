"""Akses basis data Hestia. SQLite, skema kompatibel Postgres."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "hestia.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS targets (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  domain      TEXT NOT NULL UNIQUE,
  tipe        TEXT NOT NULL DEFAULT 'lain',
  status      TEXT NOT NULL DEFAULT 'kandidat',
  owner       TEXT NOT NULL DEFAULT '',
  tags        TEXT NOT NULL DEFAULT '',
  catatan     TEXT NOT NULL DEFAULT '',
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_targets_status ON targets(status);
"""

def conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c

def init():
    with conn() as c:
        c.executescript(SCHEMA)

def row_to_dict(r):
    return dict(r)
