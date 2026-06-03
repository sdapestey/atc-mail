"""Registro de mensajes ya procesados (idempotencia)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from atc_mail.config import processed_db_path


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_messages (
            message_id TEXT PRIMARY KEY,
            imap_uid TEXT,
            cto TEXT,
            processed_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    return conn


def is_processed(message_id: str, imap_uid: str | None = None) -> bool:
    if not message_id and not imap_uid:
        return False
    db_path = processed_db_path()
    with _connect(db_path) as conn:
        if message_id:
            row = conn.execute(
                "SELECT 1 FROM processed_messages WHERE message_id = ?",
                (message_id,),
            ).fetchone()
            if row:
                return True
        if imap_uid:
            row = conn.execute(
                "SELECT 1 FROM processed_messages WHERE imap_uid = ?",
                (imap_uid,),
            ).fetchone()
            if row:
                return True
    return False


def mark_processed(message_id: str, imap_uid: str | None, cto: str) -> None:
    db_path = processed_db_path()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO processed_messages (message_id, imap_uid, cto)
            VALUES (?, ?, ?)
            """,
            (message_id or f"uid:{imap_uid}", imap_uid, cto),
        )
        conn.commit()
