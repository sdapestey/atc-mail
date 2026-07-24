"""Tests de parseo IMAP (headers, sin conexión real)."""
from __future__ import annotations

from atc_mail.mail_imap import _extract_header_bytes, inbound_from_header_bytes


def test_inbound_from_header_bytes():
    raw = (
        b"From: Sebastian <sebastian.apestey-ext@americantower.com>\r\n"
        b"To: noc.atc.arg@gmail.com\r\n"
        b"Cc: lucas.gimenez@americantower.com\r\n"
        b"Subject: TIMBRADO CTO TG02-FATC-8-103620\r\n"
        b"Message-ID: <abc123@mail.gmail.com>\r\n"
        b"In-Reply-To: \r\n"
        b"References: \r\n"
        b"\r\n"
    )
    mail = inbound_from_header_bytes("42", raw)
    assert mail.imap_uid == "42"
    assert mail.message_id == "<abc123@mail.gmail.com>"
    assert "sebastian.apestey-ext@americantower.com" in mail.from_header.lower()
    assert "TIMBRADO CTO TG02-FATC-8-103620" in mail.subject.upper()
    assert "lucas.gimenez@americantower.com" in mail.cc_header.lower()
    assert mail.in_reply_to.strip() == ""
    assert mail.references.strip() == ""


def test_inbound_reaction_headers():
    raw = (
        b"From: User <user@americantower.com>\r\n"
        b"Subject: Re: TIMBRADO CTO SI01-FATC-8-101093\r\n"
        b"Message-ID: <react@outlook.com>\r\n"
        b"In-Reply-To: <orig@gmail.com>\r\n"
        b"References: <orig@gmail.com>\r\n"
        b"\r\n"
    )
    mail = inbound_from_header_bytes("7", raw)
    assert mail.in_reply_to == "<orig@gmail.com>"
    assert "<orig@gmail.com>" in mail.references


def test_extract_header_bytes_tuple_payload():
    headers = b"Subject: TIMBRADO CTO X\r\n\r\n"
    data = [(b"1 (BODY[HEADER] {24}", headers)]
    assert _extract_header_bytes(data) == headers


def test_extract_header_bytes_empty():
    assert _extract_header_bytes([]) is None
    assert _extract_header_bytes([b"OK"]) is None
