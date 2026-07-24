"""Lectura de correo vía IMAP."""
from __future__ import annotations

import email
import imaplib
import logging
import re
from contextlib import contextmanager
from dataclasses import dataclass
from email.header import decode_header, make_header
from typing import Iterator

from atc_mail.config import get_mail_config

logger = logging.getLogger(__name__)

_FETCH_HEADER_RE = re.compile(
    rb"BODY\[HEADER\](?:<\d+>)?\s*\{(\d+)\}\r?\n",
    re.IGNORECASE,
)


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


@contextmanager
def imap_session() -> Iterator[imaplib.IMAP4_SSL]:
    """Una sola sesión IMAP (login → select INBOX → logout)."""
    client = _connect_imap()
    try:
        status, _ = client.select("INBOX")
        if status != "OK":
            raise RuntimeError("No se pudo seleccionar INBOX")
        yield client
    finally:
        try:
            client.logout()
        except imaplib.IMAP4.error:
            pass


def _extract_header_bytes(fetch_data: list | tuple) -> bytes | None:
    """Extrae bytes de cabecera desde la respuesta de UID FETCH BODY.PEEK[HEADER]."""
    for item in fetch_data:
        if not isinstance(item, tuple) or len(item) < 2:
            continue
        payload = item[1]
        if isinstance(payload, (bytes, bytearray)) and payload:
            return bytes(payload)
        if isinstance(item[0], (bytes, bytearray)):
            m = _FETCH_HEADER_RE.search(item[0])
            if m and isinstance(payload, (bytes, bytearray)):
                return bytes(payload)
    return None


def inbound_from_header_bytes(imap_uid: str, raw_headers: bytes) -> InboundMail:
    msg = email.message_from_bytes(raw_headers)
    return InboundMail(
        imap_uid=imap_uid,
        message_id=(msg.get("Message-ID") or "").strip(),
        from_header=_decode_header_value(msg.get("From")),
        to_header=_decode_header_value(msg.get("To")),
        cc_header=_decode_header_value(msg.get("Cc")),
        subject=_decode_header_value(msg.get("Subject")),
        in_reply_to=_decode_header_value(msg.get("In-Reply-To")),
        references=_decode_header_value(msg.get("References")),
    )


def fetch_timbrado_mails(client: imaplib.IMAP4_SSL) -> list[InboundMail]:
    """
    Solo UNSEEN con asunto TIMBRADO CTO.

    Usa BODY.PEEK[HEADER] (sin body, sin marcar Seen al leer).
    Los ya respondidos quedan \\Seen y no se vuelven a bajar.
    """
    status, data = client.uid("search", None, '(UNSEEN SUBJECT "TIMBRADO CTO")')
    if status != "OK" or not data or not data[0]:
        return []

    mails: list[InboundMail] = []
    for uid in data[0].split():
        uid_s = uid.decode() if isinstance(uid, bytes) else str(uid)
        status, msg_data = client.uid("fetch", uid_s, "(BODY.PEEK[HEADER])")
        if status != "OK" or not msg_data:
            logger.warning("No se pudo fetch headers UID=%s", uid_s)
            continue
        raw = _extract_header_bytes(msg_data)
        if not raw:
            logger.warning("Headers vacíos UID=%s", uid_s)
            continue
        mails.append(inbound_from_header_bytes(uid_s, raw))
    return mails


def fetch_unseen_mails() -> list[InboundMail]:
    """Compat: abre sesión, lista UNSEEN TIMBRADO CTO y cierra."""
    with imap_session() as client:
        return fetch_timbrado_mails(client)


def mark_seen(client: imaplib.IMAP4_SSL, imap_uid: str) -> None:
    """Marca \\Seen usando la sesión abierta (UID STORE)."""
    uid = imap_uid.encode() if isinstance(imap_uid, str) else imap_uid
    status, _ = client.uid("store", uid, "+FLAGS", r"(\Seen)")
    if status != "OK":
        logger.warning("No se pudo marcar Seen UID=%s", imap_uid)


def mark_seen_many(client: imaplib.IMAP4_SSL, imap_uids: list[str]) -> None:
    if not imap_uids:
        return
    # Un STORE por UID es fiable en Gmail; evita límites de set size.
    for uid in imap_uids:
        mark_seen(client, uid)
