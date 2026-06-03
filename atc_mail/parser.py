"""Parser de asunto TIMBRADO CTO."""
from __future__ import annotations

import re

TIMBRADO_SUBJECT_RE = re.compile(
    r"^\s*TIMBRADO\s+CTO\s+(?P<cto>[A-Za-z0-9]+-FATC-\d+-\d+)\s*$",
    re.IGNORECASE,
)

_REPLY_PREFIX_RE = re.compile(r"^\s*(?:re|fw|fwd)\s*:\s*", re.IGNORECASE)


def normalize_subject(subject: str | None) -> str:
    s = (subject or "").strip()
    while True:
        m = _REPLY_PREFIX_RE.match(s)
        if not m:
            break
        s = s[m.end() :].strip()
    return s


def parse_timbrado_subject(subject: str | None) -> str | None:
    m = TIMBRADO_SUBJECT_RE.match(normalize_subject(subject))
    if not m:
        return None
    return m.group("cto").upper()
