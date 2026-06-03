#!/usr/bin/env python3
"""Una pasada del worker (prueba manual o cron)."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atc_mail.worker import _setup_logging, process_once  # noqa: E402


def main() -> int:
    _setup_logging()
    n = process_once()
    logging.getLogger(__name__).info("Procesados en esta pasada: %d", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
