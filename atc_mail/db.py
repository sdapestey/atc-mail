"""Conexión PostgreSQL (solo lectura)."""
from __future__ import annotations

from contextlib import contextmanager

import psycopg2

from atc_mail.config import get_db_params


@contextmanager
def db_cursor():
    params = get_db_params()
    conn = psycopg2.connect(connect_timeout=10, **params)
    try:
        with conn.cursor() as cur:
            yield cur
    finally:
        conn.close()
