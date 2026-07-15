"""Historial de consultas de timbrado en CSV (exportable a Excel)."""
from __future__ import annotations

import csv
import logging
from datetime import datetime
from email.utils import parseaddr
from pathlib import Path
from zoneinfo import ZoneInfo

from atc_mail.config import timbrado_historico_csv_path
from atc_mail.sites import site_from_cto

logger = logging.getLogger(__name__)

_BA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")

CSV_HEADERS = (
    "consulted_at",
    "sender_email",
    "sender_name",
    "cto",
    "site",
    "reply_to",
    "reply_cc",
    "message_id",
    "status",
)


def parse_sender(from_header: str | None) -> tuple[str, str]:
    """Devuelve (email, nombre) a partir del header From."""
    name, addr = parseaddr(from_header or "")
    return (addr or "").strip(), (name or "").strip()


def now_buenos_aires_iso() -> str:
    """Fecha/hora actual en America/Argentina/Buenos_Aires (ISO 8601 con offset)."""
    return datetime.now(_BA_TZ).isoformat(timespec="seconds")


def append_query_log(
    *,
    from_header: str | None,
    cto: str,
    reply_to: str = "",
    reply_cc: str = "",
    message_id: str = "",
    status: str = "sent",
    site: str | None = None,
    csv_path: Path | None = None,
) -> Path:
    """
    Appendea una fila al CSV de historial.

    consulted_at se guarda en hora de Buenos Aires (ISO 8601 con offset, ej. -03:00).
    Crea el archivo con header si no existe.
    """
    path = csv_path or timbrado_historico_csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    sender_email, sender_name = parse_sender(from_header)
    consulted_at = now_buenos_aires_iso()
    site_val = site if site is not None else site_from_cto(cto)

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
                "site": site_val,
                "reply_to": reply_to,
                "reply_cc": reply_cc,
                "message_id": message_id,
                "status": status,
            }
        )
    return path
