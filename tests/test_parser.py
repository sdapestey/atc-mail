from atc_mail.parser import parse_timbrado_subject


def test_parse_valid_subject():
    assert parse_timbrado_subject("TIMBRADO CTO ES01-FATC-8-105270") == "ES01-FATC-8-105270"


def test_parse_valid_subject_lowercase():
    assert parse_timbrado_subject("timbrado cto tg01-fatc-1-000987") == "TG01-FATC-1-000987"


def test_parse_subject_with_re_prefix():
    assert (
        parse_timbrado_subject("Re: timbrado cto es01-fatc-8-105270")
        == "ES01-FATC-8-105270"
    )


def test_parse_valid_subject_with_spaces():
    assert parse_timbrado_subject("  TIMBRADO CTO ES01-FATC-8-105270  ") == "ES01-FATC-8-105270"


def test_parse_invalid_extra_text():
    assert parse_timbrado_subject("TIMBRADO CTO ES01-FATC-8-105270 extra") is None


def test_parse_invalid_missing_fatc():
    assert parse_timbrado_subject("TIMBRADO CTO ES01-RATC-0-0001") is None


def test_parse_invalid_empty():
    assert parse_timbrado_subject("") is None
    assert parse_timbrado_subject(None) is None


def test_parse_invalid_prefix_only():
    assert parse_timbrado_subject("Consulta timbrado ES01-FATC-8-105270") is None
