from atc_mail.parser import is_standalone_timbrado_request, parse_timbrado_subject


def test_parse_valid_subject():
    assert parse_timbrado_subject("TIMBRADO CTO ES01-FATC-8-105270") == "ES01-FATC-8-105270"


def test_parse_valid_subject_with_suffix():
    assert (
        parse_timbrado_subject("TIMBRADO CTO SM02-FATC-7-050321-TE")
        == "SM02-FATC-7-050321-TE"
    )
    assert (
        parse_timbrado_subject("timbrado cto sm02-fatc-7-050321-te")
        == "SM02-FATC-7-050321-TE"
    )
    assert (
        parse_timbrado_subject("TIMBRADO CTO SF01-FATC-7-040052-PB")
        == "SF01-FATC-7-040052-PB"
    )
    assert (
        parse_timbrado_subject("TIMBRADO CTO SF01-FATC-7-050416-P12")
        == "SF01-FATC-7-050416-P12"
    )
    assert (
        parse_timbrado_subject("TIMBRADO CTO VL01-FATC-7-010109-E")
        == "VL01-FATC-7-010109-E"
    )
    assert (
        parse_timbrado_subject("TIMBRADO CTO SM02-FATC-7-010012")
        == "SM02-FATC-7-010012"
    )
    assert (
        parse_timbrado_subject("TIMBRADO CTO SI01-FATC-7-010526-AZ")
        == "SI01-FATC-7-010526-AZ"
    )


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


def test_standalone_request_with_te_suffix():
    assert is_standalone_timbrado_request(
        "TIMBRADO CTO SM02-FATC-7-050321-TE",
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
