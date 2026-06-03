"""Firma HTML/texto para respuestas de timbrado (plantilla American Tower)."""
from __future__ import annotations

import os
from html import escape
from pathlib import Path

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_LOGO_CANDIDATES = (
    _STATIC_DIR / "atc-signature-logo.png",
    _STATIC_DIR / "atc-signature-logo.jpg",
)

# Colores firma (hex para Outlook / Gmail; equiv. a rgb del CSS corporativo)
_COLOR_NAME = "#D0DDFF"  # rgb(208, 221, 255)
_COLOR_COMPANY = "#FF9A9C"  # rgb(255, 154, 156)
_COLOR_DETAIL = "#A8C5FF"  # rgb(168, 197, 255)

_TD_BASE = "margin:0;border:0;mso-line-height-rule:exactly;"
_STYLE_NAME = (
    f"{_TD_BASE}padding:0 0 4px 0;font-family:Calibri,sans-serif;font-size:11pt;"
    f"line-height:15pt;color:{_COLOR_NAME} !important;"
)
_STYLE_COMPANY = (
    f"{_TD_BASE}padding:0 0 4px 0;font-family:Calibri,sans-serif;font-size:11pt;"
    f"line-height:15pt;color:{_COLOR_COMPANY} !important;"
)
_STYLE_DETAIL = (
    f'{_TD_BASE}padding:0 0 4px 0;font-family:"Times New Roman",Times,serif;'
    f"font-size:9pt;line-height:13pt;color:{_COLOR_DETAIL} !important;"
)

LOGO_CID = "atc-logo"


def get_signature_settings() -> dict[str, str]:
    mail_user = os.environ.get("MAIL_USER", "").strip()
    return {
        "from_name": os.environ.get("MAIL_FROM_NAME", "NOC Bot").strip() or "NOC Bot",
        "display_name": os.environ.get("MAIL_SIGNATURE_NAME", "NOC Bot").strip()
        or "NOC Bot",
        "company": os.environ.get(
            "MAIL_SIGNATURE_COMPANY", "American Tower Corporation"
        ).strip()
        or "American Tower Corporation",
        "address_line1": os.environ.get(
            "MAIL_SIGNATURE_ADDRESS_LINE1",
            "Avda. del Libertador 101 – Piso 19",
        ).strip()
        or "Avda. del Libertador 101 – Piso 19",
        "address_line2": os.environ.get(
            "MAIL_SIGNATURE_ADDRESS_LINE2", "Complejo Alrío – Torre Sur"
        ).strip()
        or "Complejo Alrío – Torre Sur",
        "address_line3": os.environ.get(
            "MAIL_SIGNATURE_ADDRESS_LINE3",
            "Vicente López, Buenos Aires – Argentina",
        ).strip()
        or "Vicente López, Buenos Aires – Argentina",
        "phone": os.environ.get(
            "MAIL_SIGNATURE_PHONE", "NOC Office: +5411 21583591"
        ).strip()
        or "NOC Office: +5411 21583591",
        "email": os.environ.get(
            "MAIL_SIGNATURE_EMAIL", "noc_atc@americantower.com"
        ).strip()
        or "noc_atc@americantower.com",
    }


def signature_logo_path() -> Path | None:
    for path in _LOGO_CANDIDATES:
        if path.is_file():
            return path
    return None


def signature_logo_mime_subtype(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "jpeg"
    return "png"


def signature_text() -> str:
    s = get_signature_settings()
    lines = [
        "",
        "--",
        s["display_name"],
        s["company"],
        s["address_line1"],
        s["address_line2"],
        s["address_line3"],
        s["phone"],
    ]
    if s["email"]:
        lines.append(f"Email: {s['email']}")
    return "\n".join(lines)


def _font(
    text: str, *, color: str, face: str, size_pt: str, line_height_pt: str | None = None
) -> str:
    """<font> legacy: Outlook respeta color/face cuando ignora CSS en spans."""
    lh = line_height_pt or size_pt
    return (
        f'<font color="{color}" face="{face}" '
        f'style="font-size:{size_pt};line-height:{lh};">'
        f"{escape(text)}</font>"
    )


def _sig_row(
    text: str,
    td_style: str,
    *,
    color: str,
    face: str,
    size_pt: str,
    line_height_pt: str | None = None,
) -> str:
    return (
        "<tr><td "
        f'style="{td_style}">'
        f"{_font(text, color=color, face=face, size_pt=size_pt, line_height_pt=line_height_pt)}"
        "</td></tr>"
    )


def signature_html() -> str:
    s = get_signature_settings()
    rows = [
        _sig_row(
            s["display_name"],
            _STYLE_NAME,
            color=_COLOR_NAME,
            face="Calibri",
            size_pt="11pt",
            line_height_pt="15pt",
        ),
        _sig_row(
            s["company"],
            _STYLE_COMPANY,
            color=_COLOR_COMPANY,
            face="Calibri",
            size_pt="11pt",
            line_height_pt="15pt",
        ),
        _sig_row(
            s["address_line1"],
            _STYLE_DETAIL,
            color=_COLOR_DETAIL,
            face="Times New Roman",
            size_pt="9pt",
            line_height_pt="13pt",
        ),
        _sig_row(
            s["address_line2"],
            _STYLE_DETAIL,
            color=_COLOR_DETAIL,
            face="Times New Roman",
            size_pt="9pt",
            line_height_pt="13pt",
        ),
        _sig_row(
            s["address_line3"],
            _STYLE_DETAIL,
            color=_COLOR_DETAIL,
            face="Times New Roman",
            size_pt="9pt",
            line_height_pt="13pt",
        ),
        _sig_row(
            s["phone"],
            _STYLE_DETAIL,
            color=_COLOR_DETAIL,
            face="Times New Roman",
            size_pt="9pt",
            line_height_pt="13pt",
        ),
    ]
    if s["email"]:
        mail = escape(s["email"])
        rows.append(
            "<tr><td "
            f'style="{_STYLE_DETAIL}">'
            f'<font color="{_COLOR_DETAIL}" face="Times New Roman" '
            'style="font-size:9pt;line-height:13pt;">'
            "Email: "
            f'<a href="mailto:{mail}" style="color:{_COLOR_DETAIL} !important;'
            "font-family:'Times New Roman',Times,serif;font-size:9pt;"
            f'text-decoration:underline;">{mail}</a></font></td></tr>'
        )

    logo_row = ""
    if signature_logo_path():
        logo_row = (
            "<tr><td style=\"padding:8px 0 0;margin:0;\">"
            f'<img src="cid:{LOGO_CID}" alt="American Tower" width="300" '
            'style="display:block;border:0;max-width:300px;height:auto;" />'
            "</td></tr>"
        )

    return (
        '<div style="margin-top:24px;padding-top:16px;border-top:1px solid #d9d9d9;">'
        '<table cellpadding="0" cellspacing="0" border="0" role="presentation" '
        'style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">'
        + "".join(rows)
        + logo_row
        + "</table></div>"
    )
