"""Configuración vía variables de entorno."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


def _database_from_url(url: str) -> dict:
    p = urlparse(url)
    if p.scheme not in ("postgresql", "postgres"):
        raise ValueError("DATABASE_URL debe ser postgresql://...")
    path = (p.path or "").lstrip("/")
    return {
        "dbname": path or "postgres",
        "user": p.username or "",
        "password": p.password or "",
        "host": p.hostname or "localhost",
        "port": str(p.port or 5432),
    }


def get_db_params() -> dict:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return _database_from_url(url)
    return {
        "dbname": os.environ.get("DB_NAME", "postgres"),
        "user": os.environ.get("DB_USER", "om_read"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": os.environ.get("DB_PORT", "5432"),
    }


def get_mail_config() -> dict:
    return {
        "imap_host": os.environ.get("MAIL_IMAP_HOST", "outlook.office365.com").strip(),
        "imap_port": int(os.environ.get("MAIL_IMAP_PORT", "993")),
        "smtp_host": os.environ.get("MAIL_SMTP_HOST", "smtp.office365.com").strip(),
        "smtp_port": int(os.environ.get("MAIL_SMTP_PORT", "587")),
        "user": os.environ.get(
            "MAIL_USER", "sebastian.apestey@americantower.com"
        ).strip(),
        "password": os.environ.get("MAIL_PASSWORD", ""),
    }


def get_allowed_sender_domains() -> frozenset[str]:
    raw = os.environ.get("MAIL_ALLOWED_SENDER_DOMAINS", "").strip()
    if not raw:
        return frozenset()
    return frozenset(d.strip().lower() for d in raw.split(",") if d.strip())


def poll_interval_seconds() -> int:
    return max(10, int(os.environ.get("POLL_INTERVAL_SECONDS", "60")))


def dry_run() -> bool:
    return os.environ.get("DRY_RUN", "0").strip().lower() in ("1", "true", "yes")


def processed_db_path() -> Path:
    raw = os.environ.get("PROCESSED_DB_PATH", "./data/processed.db").strip()
    return Path(raw).expanduser().resolve()


def log_level() -> str:
    return os.environ.get("LOG_LEVEL", "INFO").strip().upper()
