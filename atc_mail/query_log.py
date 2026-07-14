"""Historial de consultas de timbrado en CSV (exportable a Excel)."""
from __future__ import annotations

import csv
import logging
from datetime import datetime, timezone
from email.utils import parseaddr
from pathlib import Path

from atc_mail.config import timbrado_queries_csv_path

logger = logging.getLogger(__name__)

CSV_HEADERS = (
    "consulted_at",
    "sender_email",
    "sender_name",
    "cto",
    "ports_found",
    "reply_to",
    "reply_cc",
    "message_id",
    "status",
)


def parse_sender(from_header: str | None) -> tuple[str, str]:
    """Devuelve (email, nombre) a partir del header From."""
    name, addr = parseaddr(from_header or "")
    return (addr or "").strip(), (name or "").strip()


def append_query_log(
    *,
    from_header: str | None,
    cto: str,
    ports_found: int,
    reply_to: str = "",
    reply_cc: str = "",
    message_id: str = "",
    status: str = "sent",
    csv_path: Path | None = None,
) -> Path:
    """
    Appendea una fila al CSV de historial.

    consulted_at se guarda en UTC (ISO 8601 con sufijo Z).
    Crea el archivo con header si no existe.
    """
    path = csv_path or timbrado_queries_csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    sender_email, sender_name = parse_sender(from_header)
    consulted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "consulted_at": consulted_at,
                "sender_email": sender_email,
                "sender_name": sender_name,
                "cto": cto,
                "ports_found": ports_found,
                "reply_to": reply_to,
                "reply_cc": reply_cc,
                "message_id": message_id,
                "status": status,
            }
        )
    return path
