from atc_mail.cto_inventory import (
    CtoPortRow,
    CtoUbicacion,
    build_timbrado_reply,
    format_timbrado_reply,
)


def test_format_empty_cto():
    ubicacion = CtoUbicacion(direccion=None, lat=None, lon=None)
    body = format_timbrado_reply("ES01-FATC-8-999999", [], ubicacion=ubicacion)
    assert "Sin registros para ES01-FATC-8-999999" in body
    assert "FREE / RESERVED / IN SERVICE" in body


def test_format_table_with_mixed_statuses():
    rows = [
        CtoPortRow(out=1, aid="1058516041", status="IN SERVICE", operador="TASA"),
        CtoPortRow(out=2, aid="-", status="FREE", operador="-"),
        CtoPortRow(out=3, aid="1058516042", status="RESERVED", operador="TASA"),
    ]
    ubicacion = CtoUbicacion(
        direccion="Av. Siempre Viva 742 (BA San Fernando)",
        lat=-34.472252,
        lon=-58.51101,
    )
    body = format_timbrado_reply("ES01-FATC-8-105270", rows, ubicacion=ubicacion)
    assert "Timbrado CTO — ES01-FATC-8-105270" in body
    assert "Fuente: inventario (FREE / RESERVED / IN SERVICE)" in body
    assert "Dirección: Av. Siempre Viva 742 (BA San Fernando)" in body
    assert "Abrir en Maps:" in body
    assert "google.com/maps" in body
    assert "Coordenadas: -34.472252, -58.51101" in body
    assert "OUT 1 · AID 1058516041" in body
    assert "FREE" in body
    assert "1058516042" in body
    assert "RESERVED" in body
    assert "NOC ATC — respuesta automática" in body
    header_block = body.split("Puertos:")[0]
    assert "\n\n" not in header_block.strip()

    html = build_timbrado_reply(
        "ES01-FATC-8-105270", rows, ubicacion=ubicacion
    ).html
    assert "<table" in html
    assert "<th" in html and "OUT</th>" in html
    assert "1058516041" in html
    assert "Abrir en Maps" in html
    assert html.count("<p>") == 0 or "Timbrado CTO" in html
    assert "NOC Bot" in html
    assert "#D0DDFF" in html


def test_format_hides_non_tasa_as_ocupado():
    rows = [
        CtoPortRow(out=1, aid="1051563426", status="IN SERVICE", operador="TASA"),
        CtoPortRow(out=5, aid="123086340", status="IN SERVICE", operador="DIRECTV"),
        CtoPortRow(out=8, aid="127711116", status="IN SERVICE", operador="DIRECTV"),
        CtoPortRow(out=2, aid="-", status="FREE", operador="-"),
    ]
    ubicacion = CtoUbicacion(direccion=None, lat=None, lon=None)
    body = format_timbrado_reply("TG02-FATC-8-103620", rows, ubicacion=ubicacion)
    assert "OUT 1 · AID 1051563426 · IN SERVICE · TASA" in body
    assert "OUT 5 · OCUPADO" in body
    assert "OUT 8 · OCUPADO" in body
    assert "OUT 2 · AID - · FREE · -" in body
    assert "DIRECTV" not in body
    assert "123086340" not in body
    assert "127711116" not in body

    html = build_timbrado_reply(
        "TG02-FATC-8-103620", rows, ubicacion=ubicacion
    ).html
    assert "colspan=\"3\"" in html
    assert "OCUPADO" in html
    assert "DIRECTV" not in html
    assert "123086340" not in html
    assert "1051563426" in html
    assert "TASA" in html
