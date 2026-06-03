"""Destinatarios de respuesta (From + Cc)."""
from __future__ import annotations

from email.utils import formataddr, getaddresses

from atc_mail.config import get_mail_config


def collect_reply_recipients(
    from_header: str | None,
    cc_header: str | None,
) -> list[str]:
    """From + Cc, sin duplicados ni el buzón propio. Devuelve valores para header To."""
    own = get_mail_config()["user"].strip().lower()
    seen: set[str] = set()
    to_values: list[str] = []

    for name, addr in getaddresses([from_header or "", cc_header or ""]):
        email = (addr or "").strip()
        key = email.lower()
        if not email or key == own or key in seen:
            continue
        seen.add(key)
        to_values.append(formataddr((name, email)) if name else email)

    return to_values
