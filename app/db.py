"""
Simple SQLite persistence for ingested user documents.

Provides init_db(path), save_doc(db_path, metadata), get_docs_by_user(db_path, user_id)
This is a small wrapper using the stdlib sqlite3 for portability.
"""
import sqlite3
import json
from typing import Dict, List, Optional


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    text TEXT NOT NULL,
    total_income REAL,
    total_expenses REAL,
    savings_goal REAL,
    metadata_json TEXT
);
"""


def init_db(db_path: str = "data/db.sqlite"):
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(docs)")
    cols = [r[1] for r in cur.fetchall()]
    if 'created_at' not in cols:
        try:
            cur.execute("ALTER TABLE docs ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
        except Exception:
            pass
    conn.close()


def save_doc(db_path: str, metadata: Dict):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO docs (user_id, text, total_income, total_expenses, savings_goal, metadata_json) VALUES (?, ?, ?, ?, ?, ?)",
        (
            metadata.get("user_id"),
            metadata.get("text"),
            metadata.get("total_income"),
            metadata.get("total_expenses"),
            metadata.get("savings_goal"),
            json.dumps(metadata),
        ),
    )
    conn.commit()
    conn.close()


def get_docs_by_user(db_path: str, user_id: str) -> List[Dict]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, text, total_income, total_expenses, savings_goal, metadata_json FROM docs WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    results = []
    for r in rows:
        meta = {}
        try:
            meta = json.loads(r[6]) if r[6] else {}
        except Exception:
            meta = {}
        results.append({
            "id": r[0],
            "user_id": r[1],
            "text": r[2],
            "total_income": r[3],
            "total_expenses": r[4],
            "savings_goal": r[5],
            "metadata": meta,
        })
    return results


def list_users(db_path: str) -> List[str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT user_id FROM docs")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]
