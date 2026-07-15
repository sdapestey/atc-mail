"""Tests del historial CSV de consultas de timbrado."""
from __future__ import annotations

import csv

from atc_mail.config import timbrado_queries_csv_path
from atc_mail.query_log import CSV_HEADERS, append_query_log, parse_sender
from atc_mail.sites import site_from_cto


def test_parse_sender_with_name():
    email, name = parse_sender("Sebastian Apestey <sebastian.apestey-ext@americantower.com>")
    assert email == "sebastian.apestey-ext@americantower.com"
    assert name == "Sebastian Apestey"


def test_parse_sender_email_only():
    email, name = parse_sender("user@tmoviles.com.ar")
    assert email == "user@tmoviles.com.ar"
    assert name == ""


def test_parse_sender_empty():
    email, name = parse_sender(None)
    assert email == ""
    assert name == ""


def test_site_from_cto_known():
    assert site_from_cto("SI01-FATC-8-101093") == "San Isidro"
    assert site_from_cto("sf01-fatc-8-102732") == "San Fernando"
    assert site_from_cto("TG01-FATC-8-109725") == "Tigre"
    assert site_from_cto("ES01-FATC-8-105270") == "Escobar"
    assert site_from_cto("MO01-FATC-8-1") == "Moreno"


def test_site_from_cto_unknown():
    assert site_from_cto("XX01-FATC-8-1") == ""
    assert site_from_cto("") == ""
    assert site_from_cto(None) == ""


def test_csv_path_default_beside_processed(monkeypatch, tmp_path):
    db = tmp_path / "data" / "processed.db"
    monkeypatch.setenv("PROCESSED_DB_PATH", str(db))
    monkeypatch.delenv("TIMBRADO_QUERIES_CSV_PATH", raising=False)
    path = timbrado_queries_csv_path()
    assert path == (tmp_path / "data" / "timbrado_queries.csv").resolve()


def test_csv_path_explicit_override(monkeypatch, tmp_path):
    custom = tmp_path / "custom" / "queries.csv"
    monkeypatch.setenv("TIMBRADO_QUERIES_CSV_PATH", str(custom))
    assert timbrado_queries_csv_path() == custom.resolve()


def test_append_creates_header_and_row(tmp_path):
    csv_file = tmp_path / "subdir" / "timbrado_queries.csv"
    path = append_query_log(
        from_header="Lucas <lucas.gimenez@americantower.com>",
        cto="TG01-FATC-8-109725",
        reply_to="lucas.gimenez@americantower.com",
        reply_cc="facundo.vergara@americantower.com",
        message_id="<abc@mail>",
        status="sent",
        csv_path=csv_file,
    )
    assert path == csv_file
    assert csv_file.exists()

    with csv_file.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    row = rows[0]
    assert list(row.keys()) == list(CSV_HEADERS)
    assert row["sender_email"] == "lucas.gimenez@americantower.com"
    assert row["sender_name"] == "Lucas"
    assert row["cto"] == "TG01-FATC-8-109725"
    assert row["site"] == "Tigre"
    assert "ports_found" not in row
    assert row["reply_to"] == "lucas.gimenez@americantower.com"
    assert row["reply_cc"] == "facundo.vergara@americantower.com"
    assert row["message_id"] == "<abc@mail>"
    assert row["status"] == "sent"
    assert row["consulted_at"].endswith("Z")


def test_append_second_row_no_duplicate_header(tmp_path):
    csv_file = tmp_path / "timbrado_queries.csv"
    append_query_log(
        from_header="a@americantower.com",
        cto="SI01-FATC-8-1",
        csv_path=csv_file,
    )
    append_query_log(
        from_header="b@americantower.com",
        cto="BB01-FATC-8-2",
        csv_path=csv_file,
    )
    text = csv_file.read_text(encoding="utf-8")
    assert text.count("consulted_at,") == 1
    with csv_file.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert rows[0]["cto"] == "SI01-FATC-8-1"
    assert rows[0]["site"] == "San Isidro"
    assert rows[1]["cto"] == "BB01-FATC-8-2"
    assert rows[1]["site"] == ""
