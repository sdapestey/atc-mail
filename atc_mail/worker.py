"""Worker principal: poll IMAP → Postgres → SMTP reply."""
from __future__ import annotations

import logging
import sys
import time

from atc_mail.config import (
    dry_run,
    get_allowed_sender_domains,
    log_level,
    poll_interval_seconds,
)
from atc_mail.cto_inventory import build_timbrado_reply, consultar_cto_puertos
from atc_mail.mail_imap import fetch_unseen_mails, mark_seen
from atc_mail.mail_smtp import send_timbrado_reply
from atc_mail.parser import parse_timbrado_subject
from atc_mail.processed import is_processed, mark_processed
from atc_mail.security import sender_allowed

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, log_level(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def process_once() -> int:
    """Procesa UNSEEN una vez. Devuelve cantidad de respuestas enviadas (o simuladas)."""
    handled = 0
    mails = fetch_unseen_mails()
    logger.info("Mails TIMBRADO CTO en bandeja: %d", len(mails))

    for inbound in mails:
        mid = inbound.message_id
        uid = inbound.imap_uid

        if is_processed(mid, uid):
            logger.debug("Ya procesado: message-id=%s uid=%s", mid, uid)
            if not dry_run():
                mark_seen(uid)
            continue

        if not sender_allowed(inbound.from_header):
            logger.info(
                "Remitente no permitido (dominios: %s), skip: %s",
                ", ".join(sorted(get_allowed_sender_domains())),
                inbound.from_header,
            )
            if not dry_run():
                mark_seen(uid)
            continue

        cto = parse_timbrado_subject(inbound.subject)
        if not cto:
            logger.debug(
                "Asunto no es TIMBRADO CTO, skip: %r",
                inbound.subject,
            )
            continue

        try:
            rows = consultar_cto_puertos(cto)
            reply = build_timbrado_reply(cto, rows)
        except Exception:
            logger.exception("Error consultando CTO %s", cto)
            continue

        logger.info(
            "Timbrado %s | from=%s | filas=%d | dry_run=%s",
            cto,
            inbound.from_header,
            len(rows),
            dry_run(),
        )

        if dry_run():
            logger.info("--- DRY RUN respuesta ---\n%s\n--- fin ---", reply.text)
            handled += 1
            continue

        try:
            send_timbrado_reply(
                inbound,
                cto=cto,
                body_text=reply.text,
                body_html=reply.html,
            )
        except Exception:
            logger.exception("Error enviando reply para CTO %s", cto)
            continue

        mark_processed(mid, uid, cto)
        mark_seen(uid)
        handled += 1

    return handled


def run_forever() -> None:
    _setup_logging()
    interval = poll_interval_seconds()
    logger.info(
        "atc-mail worker iniciado (poll=%ds, dry_run=%s)",
        interval,
        dry_run(),
    )
    while True:
        try:
            process_once()
        except Exception:
            logger.exception("Error en ciclo del worker")
        time.sleep(interval)


def main() -> None:
    run_forever()


if __name__ == "__main__":
    main()
