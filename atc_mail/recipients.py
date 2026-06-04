"""Destinatarios de respuesta: To = remitente, Cc = fijos + copia entrante permitida."""
from __future__ import annotations

from dataclasses import dataclass

from email.utils import formataddr, getaddresses, parseaddr

from atc_mail.config import get_always_cc_addresses, get_mail_config
from atc_mail.security import email_domain_allowed


@dataclass(frozen=True)
class ReplyRecipients:
    to: tuple[str, ...]
    cc: tuple[str, ...]


def _format_recipient(name: str, email: str) -> str:
    return formataddr((name, email)) if name else email


def _primary_sender(from_header: str | None) -> str | None:
    if not from_header:
        return None
    for name, addr in getaddresses([from_header]):
        email = (addr or "").strip()
        if email and email_domain_allowed(email):
            return _format_recipient(name, email)
    return None


def _addresses_from_header(header: str | None) -> list[str]:
    if not header:
        return []
    own = get_mail_config()["user"].strip().lower()
    out: list[str] = []
    seen: set[str] = set()
    for name, addr in getaddresses([header]):
        email = (addr or "").strip()
        key = email.lower()
        if not email or key == own or key in seen:
            continue
        if not email_domain_allowed(email):
            continue
        seen.add(key)
        out.append(_format_recipient(name, email))
    return out


def _email_key(formatted: str) -> str:
    _, addr = parseaddr(formatted)
    return (addr or formatted).strip().lower()


def collect_reply_recipients(
    from_header: str | None,
    cc_header: str | None,
) -> ReplyRecipients:
    """To = remitente. Cc = MAIL_ALWAYS_CC + Cc entrante permitido (sin duplicar To)."""
    to_primary = _primary_sender(from_header)
    if not to_primary:
        return ReplyRecipients(to=(), cc=())

    to_key = _email_key(to_primary)
    cc_keys: set[str] = {to_key}
    cc_list: list[str] = []

    for addr in get_always_cc_addresses():
        key = addr.strip().lower()
        if not key or key in cc_keys:
            continue
        cc_keys.add(key)
        cc_list.append(addr)

    for formatted in _addresses_from_header(cc_header):
        key = _email_key(formatted)
        if key in cc_keys:
            continue
        cc_keys.add(key)
        cc_list.append(formatted)

    return ReplyRecipients(to=(to_primary,), cc=tuple(cc_list))
