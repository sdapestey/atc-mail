from atc_mail.parser import is_standalone_timbrado_request, parse_timbrado_subject


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


def test_standalone_request_valid():
    assert is_standalone_timbrado_request(
        "TIMBRADO CTO ES01-FATC-8-105270",
        None,
        None,
    )


def test_standalone_request_reaction_reply_subject():
    assert not is_standalone_timbrado_request(
        "Re: TIMBRADO CTO ES01-FATC-8-105270",
        None,
        None,
    )


def test_standalone_request_in_reply_to():
    assert not is_standalone_timbrado_request(
        "TIMBRADO CTO ES01-FATC-8-105270",
        "<bot-msg@mail.gmail.com>",
        None,
    )


def test_standalone_request_references():
    assert not is_standalone_timbrado_request(
        "TIMBRADO CTO ES01-FATC-8-105270",
        None,
        "<original@tmoviles.com.ar>",
    )


def test_standalone_request_outlook_reaction_fallback():
    assert not is_standalone_timbrado_request(
        "RE: TIMBRADO CTO TG01-FATC-8-109380",
        "<CAB123@americantower.com>",
        "<CAB123@americantower.com> <CAB456@gmail.com>",
    )
