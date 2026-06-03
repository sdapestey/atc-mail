from atc_mail.cto_inventory import (
    CtoPortRow,
    CtoUbicacion,
    build_timbrado_reply,
    format_timbrado_reply,
)


def test_format_empty_cto():
    body = format_timbrado_reply("ES01-FATC-8-999999", [])
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
