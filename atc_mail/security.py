"""Validación de remitentes."""
from __future__ import annotations

from email.utils import parseaddr

from atc_mail.config import get_allowed_sender_domains, get_mail_config


def sender_address(from_header: str | None) -> str:
    _, addr = parseaddr(from_header or "")
    return (addr or "").strip().lower()


def is_own_mailbox(from_header: str | None) -> bool:
    addr = sender_address(from_header)
    own = get_mail_config()["user"].strip().lower()
    return bool(addr and own and addr == own)


def sender_allowed(from_header: str | None) -> bool:
    if is_own_mailbox(from_header):
        return False
    allowed = get_allowed_sender_domains()
    if not allowed:
        return True
    addr = sender_address(from_header)
    if not addr or "@" not in addr:
        return False
    domain = addr.rsplit("@", 1)[-1]
    return domain in allowed
