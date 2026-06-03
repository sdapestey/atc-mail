"""Destinatarios de respuesta (From + Cc en dominios permitidos)."""
from __future__ import annotations

from email.utils import formataddr, getaddresses

from atc_mail.config import get_mail_config
from atc_mail.security import email_domain_allowed


def collect_reply_recipients(
    from_header: str | None,
    cc_header: str | None,
) -> list[str]:
    """From + Cc solo si el dominio está permitido; sin duplicados ni buzón propio."""
    own = get_mail_config()["user"].strip().lower()
    seen: set[str] = set()
    to_values: list[str] = []
    batches: list[tuple[str, str]] = []

    if from_header:
        batches.extend(getaddresses([from_header]))
    if cc_header:
        batches.extend(getaddresses([cc_header]))

    for name, addr in batches:
        email = (addr or "").strip()
        key = email.lower()
        if not email or key == own or key in seen:
            continue
        if not email_domain_allowed(email):
            continue
        seen.add(key)
        to_values.append(formataddr((name, email)) if name else email)

    return to_values
