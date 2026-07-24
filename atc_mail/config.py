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

# Dominios remitentes permitidos si MAIL_ALLOWED_SENDER_DOMAINS no está en .env
DEFAULT_ALLOWED_SENDER_DOMAINS = "tmoviles.com.ar,retesar.com,americantower.com"

# Siempre en Cc de la respuesta (aunque no vengan en el mail entrante)
DEFAULT_ALWAYS_CC = (
    "lucas.gimenez@americantower.com,facundo.vergara@americantower.com"
)


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
        "user": os.environ.get("MAIL_USER", "").strip(),
        "password": os.environ.get("MAIL_PASSWORD", ""),
    }


def get_allowed_sender_domains() -> frozenset[str]:
    raw = os.environ.get("MAIL_ALLOWED_SENDER_DOMAINS", "").strip()
    if not raw:
        raw = DEFAULT_ALLOWED_SENDER_DOMAINS
    return frozenset(d.strip().lower() for d in raw.split(",") if d.strip())


def get_always_cc_addresses() -> tuple[str, ...]:
    raw = os.environ.get("MAIL_ALWAYS_CC", "").strip()
    if not raw:
        raw = DEFAULT_ALWAYS_CC
    return tuple(a.strip() for a in raw.split(",") if a.strip())


def poll_interval_seconds() -> int:
    return max(10, int(os.environ.get("POLL_INTERVAL_SECONDS", "30")))


def dry_run() -> bool:
    return os.environ.get("DRY_RUN", "0").strip().lower() in ("1", "true", "yes")


def processed_db_path() -> Path:
    raw = os.environ.get("PROCESSED_DB_PATH", "./data/processed.db").strip()
    return Path(raw).expanduser().resolve()


def timbrado_historico_csv_path() -> Path:
    """CSV de historial de consultas. Default: mismo directorio que processed.db."""
    raw = (
        os.environ.get("TIMBRADO_HISTORICO_CSV_PATH", "").strip()
        or os.environ.get("TIMBRADO_QUERIES_CSV_PATH", "").strip()
    )
    if raw:
        return Path(raw).expanduser().resolve()
    return processed_db_path().parent / "timbrado_historico.csv"


def log_level() -> str:
    return os.environ.get("LOG_LEVEL", "INFO").strip().upper()
