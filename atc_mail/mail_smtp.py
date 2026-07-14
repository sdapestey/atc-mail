"""Envío de respuestas vía SMTP."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from atc_mail.config import get_mail_config
from atc_mail.signature import (
    LOGO_CID,
    get_signature_settings,
    signature_logo_mime_subtype,
    signature_logo_path,
)
from atc_mail.mail_imap import InboundMail
from atc_mail.parser import parse_timbrado_subject
from atc_mail.recipients import ReplyRecipients, collect_reply_recipients

logger = logging.getLogger(__name__)


def _attach_signature_logo(msg: EmailMessage, body_html: str) -> None:
    if f"cid:{LOGO_CID}" not in body_html:
        return
    logo_path = signature_logo_path()
    if not logo_path:
        logger.warning("Logo de firma no encontrado en static/")
        return
    html_part = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_part = part
            break
    if html_part is None:
        logger.warning("No se encontró parte HTML para adjuntar logo")
        return
    html_part.add_related(
        logo_path.read_bytes(),
        maintype="image",
        subtype=signature_logo_mime_subtype(logo_path),
        cid=f"<{LOGO_CID}>",
    )


def _reply_subject(original_subject: str, cto: str) -> str:
    subj = (original_subject or "").strip()
    if subj.upper().startswith("RE:"):
        return subj
    if parse_timbrado_subject(subj):
        return f"Re: {subj}"
    return f"Re: TIMBRADO CTO {cto.upper()}"


def send_timbrado_reply(
    inbound: InboundMail,
    *,
    cto: str,
    body_text: str,
    body_html: str | None = None,
) -> ReplyRecipients:
    cfg = get_mail_config()
    if not cfg["password"]:
        raise RuntimeError("MAIL_PASSWORD no configurado")

    recipients = collect_reply_recipients(inbound.from_header, inbound.cc_header)
    if not recipients.to:
        raise ValueError("Sin remitente válido en mail entrante")

    msg = EmailMessage()
    from_name = get_signature_settings()["from_name"]
    msg["From"] = formataddr((from_name, cfg["user"]))
    msg["To"] = ", ".join(recipients.to)
    if recipients.cc:
        msg["Cc"] = ", ".join(recipients.cc)
    msg["Subject"] = _reply_subject(inbound.subject, cto)

    if inbound.message_id:
        msg["In-Reply-To"] = inbound.message_id
        refs = (inbound.references or "").strip()
        msg["References"] = f"{refs} {inbound.message_id}".strip()

    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")
        _attach_signature_logo(msg, body_html)

    with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=60) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(cfg["user"], cfg["password"])
        smtp.send_message(msg)

    logger.info(
        "SMTP reply enviado To=%s Cc=%s (CTO %s)",
        msg["To"],
        msg.get("Cc", ""),
        cto,
    )
    return recipients
