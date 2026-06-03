"""Lectura de correo vía IMAP."""
from __future__ import annotations

import email
import imaplib
import logging
from dataclasses import dataclass
from email.header import decode_header, make_header

from atc_mail.config import get_mail_config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class InboundMail:
    imap_uid: str
    message_id: str
    from_header: str
    to_header: str
    cc_header: str
    subject: str
    in_reply_to: str
    references: str


def _decode_header_value(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except (email.errors.HeaderParseError, UnicodeError):
        return str(value)


def _connect_imap() -> imaplib.IMAP4_SSL:
    cfg = get_mail_config()
    if not cfg["password"]:
        raise RuntimeError("MAIL_PASSWORD no configurado")
    client = imaplib.IMAP4_SSL(cfg["imap_host"], cfg["imap_port"])
    client.login(cfg["user"], cfg["password"])
    return client


def fetch_unseen_mails() -> list[InboundMail]:
    cfg = get_mail_config()
    client = _connect_imap()
    mails: list[InboundMail] = []
    try:
        client.select("INBOX")
        # No filtrar solo UNSEEN: tras un dry-run el mail puede quedar leído en Gmail
        # y la idempotencia (processed.db) evita reenvíos duplicados.
        status, data = client.search(None, '(SUBJECT "TIMBRADO CTO")')
        if status != "OK" or not data or not data[0]:
            return []

        for uid in data[0].split():
            uid_s = uid.decode() if isinstance(uid, bytes) else str(uid)
            status, msg_data = client.fetch(uid, "(RFC822)")
            if status != "OK" or not msg_data:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            message_id = (msg.get("Message-ID") or "").strip()
            mails.append(
                InboundMail(
                    imap_uid=uid_s,
                    message_id=message_id,
                    from_header=_decode_header_value(msg.get("From")),
                    to_header=_decode_header_value(msg.get("To")),
                    cc_header=_decode_header_value(msg.get("Cc")),
                    subject=_decode_header_value(msg.get("Subject")),
                    in_reply_to=_decode_header_value(msg.get("In-Reply-To")),
                    references=_decode_header_value(msg.get("References")),
                )
            )
    finally:
        try:
            client.logout()
        except imaplib.IMAP4.error:
            pass
    return mails


def mark_seen(imap_uid: str) -> None:
    client = _connect_imap()
    try:
        client.select("INBOX")
        client.store(imap_uid.encode() if isinstance(imap_uid, str) else imap_uid, "+FLAGS", "\\Seen")
    finally:
        try:
            client.logout()
        except imaplib.IMAP4.error:
            pass
