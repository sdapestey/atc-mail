"""Consulta inventario CTO y formateo de respuesta timbrado."""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from urllib.parse import quote_plus

from atc_mail.db import db_cursor
from atc_mail.operators import nombre_operador
from atc_mail.signature import signature_html, signature_text

_PARTIDO_DISPLAY_MAP = {
    "BA SAFE": "BA San Fernando",
    "BA ESCO": "BA Escobar",
    "BA SISI": "BA San Isidro",
    "BA VILO": "BA Vicente Lopez",
    "BA TIGR": "BA Tigre",
    "BA MORO": "BA Moreno",
    "BA MORE": "BA Moreno",
    "BA SMAR": "BA San Martin",
    "BA SAMA": "BA San Martin",
    "BA SANM": "BA San Martin",
}

ONTS_POR_CTO_SQL = """
    SELECT
        f.access_id,
        f.status,
        COALESCE(o.invocator_system, b_aid.operatorid) AS invocator_system
    FROM cm.inventory_fat_occupation f
    LEFT JOIN cm.inventory_olt_occupation o
         ON o.access_id = f.access_id
    LEFT JOIN LATERAL (
        SELECT
            CASE
                WHEN trim(b2.operatorid::text) ~ '^[0-9]+$'
                THEN trim(b2.operatorid::text)::bigint
                ELSE NULL
            END AS operatorid
        FROM aux.bajada_inventario b2
        WHERE LOWER(btrim(b2.access_id::text)) = LOWER(btrim(f.access_id::text))
        ORDER BY b2.reserved_date DESC NULLS LAST, b2.provided_date DESC NULLS LAST
        LIMIT 1
    ) b_aid ON true
    WHERE f.location_description = %s
      AND f.status IN ('IN SERVICE', 'RESERVED', 'FREE')
    ORDER BY
        COALESCE(
            f.port_number,
            NULLIF(regexp_replace(COALESCE(f.port_name, ''), '[^0-9]', '', 'g'), '')::bigint
        ) NULLS LAST,
        f.access_id
"""

CTO_COORDENADAS_SQL = """
    SELECT
        COALESCE(b.splitter_2_lat, b.ont_lat) AS lat,
        COALESCE(b.splitter_2_lon, b.ont_lon) AS lon
    FROM cm.inventory_fat_occupation f
    JOIN aux.bajada_inventario b
      ON b.access_id::text = f.access_id::text
    WHERE f.location_description = %s
      AND f.status IN ('IN SERVICE', 'RESERVED', 'FREE')
      AND (b.cto = %s OR b.cm_description = %s)
      AND COALESCE(b.splitter_2_lat, b.ont_lat) IS NOT NULL
      AND COALESCE(b.splitter_2_lon, b.ont_lon) IS NOT NULL
    ORDER BY f.access_id ASC
    LIMIT 1
"""

CTO_DIRECCION_SQL = """
    SELECT
        NULLIF(btrim(s.direccion), '') AS direccion,
        NULLIF(btrim(s.partido_despliegue), '') AS partido,
        CASE
            WHEN s.nombre_cliente = %s THEN 0
            WHEN s.nombre_atc = %s THEN 1
            ELSE 9
        END AS prio
    FROM cm.ci_sfat_mfat_bfat s
    WHERE (s.nombre_cliente = %s OR s.nombre_atc = %s)
      AND NULLIF(btrim(s.direccion), '') IS NOT NULL
    ORDER BY prio ASC
    LIMIT 1
"""


@dataclass(frozen=True)
class CtoPortRow:
    out: int
    aid: str
    status: str
    operador: str


@dataclass(frozen=True)
class CtoUbicacion:
    direccion: str | None
    lat: float | None
    lon: float | None

    @property
    def maps_url(self) -> str | None:
        if self.lat is None or self.lon is None:
            return None
        return (
            "https://www.google.com/maps/search/?api=1&query="
            + quote_plus(f"{self.lat},{self.lon}")
        )


def google_maps_url(lat: float, lon: float) -> str:
    return (
        "https://www.google.com/maps/search/?api=1&query="
        + quote_plus(f"{lat},{lon}")
    )


def consultar_cto_puertos(cto: str) -> list[CtoPortRow]:
    cto_norm = (cto or "").strip().upper()
    with db_cursor() as cur:
        cur.execute(ONTS_POR_CTO_SQL, (cto_norm,))
        rows = cur.fetchall()

    out: list[CtoPortRow] = []
    for idx, row in enumerate(rows, start=1):
        access_id, status, invocator = row[0], row[1], row[2]
        st_u = str(status or "").strip().upper()
        if st_u == "FREE":
            aid = "-"
            operador = "-"
        else:
            aid = str(access_id) if access_id is not None else "-"
            operador = nombre_operador(invocator)
        out.append(CtoPortRow(out=idx, aid=aid, status=st_u or "—", operador=operador))
    return out


def _format_direccion_postal(direccion: str, partido: str | None) -> str:
    dir_norm = " ".join(str(direccion).replace(",", " ").split())
    partido_norm = str(partido or "").strip()
    if partido_norm:
        partido_norm = _PARTIDO_DISPLAY_MAP.get(partido_norm.upper(), partido_norm)
        return f"{dir_norm} ({partido_norm})"
    return dir_norm


def consultar_cto_ubicacion(cto: str) -> CtoUbicacion:
    cto_norm = (cto or "").strip().upper()
    if not cto_norm:
        return CtoUbicacion(direccion=None, lat=None, lon=None)

    direccion: str | None = None
    lat: float | None = None
    lon: float | None = None

    with db_cursor() as cur:
        cur.execute(CTO_DIRECCION_SQL, (cto_norm, cto_norm, cto_norm, cto_norm))
        row_dir = cur.fetchone()
        if row_dir and row_dir[0]:
            direccion = _format_direccion_postal(row_dir[0], row_dir[1])

        cur.execute(CTO_COORDENADAS_SQL, (cto_norm, cto_norm, cto_norm))
        row_coord = cur.fetchone()
        if row_coord and row_coord[0] is not None and row_coord[1] is not None:
            lat = float(row_coord[0])
            lon = float(row_coord[1])

    return CtoUbicacion(direccion=direccion, lat=lat, lon=lon)


def _format_header_lines(cto_norm: str, ubicacion: CtoUbicacion) -> list[str]:
    dir_txt = ubicacion.direccion or "—"
    maps_url = ubicacion.maps_url
    if maps_url:
        direccion_line = f"Dirección: {dir_txt} Abrir en Maps: {maps_url}"
    else:
        direccion_line = f"Dirección: {dir_txt}"

    if ubicacion.lat is not None and ubicacion.lon is not None:
        coord_line = f"Coordenadas: {ubicacion.lat}, {ubicacion.lon}"
    else:
        coord_line = "Coordenadas:"

    return [
        f"Timbrado CTO — {cto_norm}",
        "Fuente: inventario (FREE / RESERVED / IN SERVICE)",
        direccion_line,
        coord_line,
        "NOC ATC — respuesta automática",
    ]


@dataclass(frozen=True)
class TimbradoReply:
    text: str
    html: str


def _resolve_ubicacion(cto: str, ubicacion: CtoUbicacion | None) -> tuple[str, CtoUbicacion]:
    cto_norm = (cto or "").strip().upper()
    if ubicacion is None:
        ubicacion = consultar_cto_ubicacion(cto_norm)
    return cto_norm, ubicacion


def _format_ports_text(rows: list[CtoPortRow]) -> list[str]:
    lines = ["Puertos:"]
    for r in rows:
        lines.append(f"  OUT {r.out} · AID {r.aid} · {r.status} · {r.operador}")
    return lines


def _format_ports_html(rows: list[CtoPortRow]) -> str:
    body_rows = []
    for r in rows:
        body_rows.append(
            "<tr>"
            f'<td style="padding:6px 10px;border:1px solid #ccc;text-align:center;">{r.out}</td>'
            f'<td style="padding:6px 10px;border:1px solid #ccc;">{escape(r.aid)}</td>'
            f'<td style="padding:6px 10px;border:1px solid #ccc;">{escape(r.status)}</td>'
            f'<td style="padding:6px 10px;border:1px solid #ccc;">{escape(r.operador)}</td>'
            "</tr>"
        )
    return (
        '<table style="border-collapse:collapse;margin-top:12px;font-size:14px;">'
        "<thead><tr style=\"background:#f3f4f6;\">"
        '<th style="padding:8px 10px;border:1px solid #ccc;">OUT</th>'
        '<th style="padding:8px 10px;border:1px solid #ccc;">AID</th>'
        '<th style="padding:8px 10px;border:1px solid #ccc;">STATUS</th>'
        '<th style="padding:8px 10px;border:1px solid #ccc;">Operador</th>'
        "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table>"
    )


def _header_row_html(content: str, *, em: bool = False, last: bool = False) -> str:
    tag_open = "<em>" if em else ""
    tag_close = "</em>" if em else ""
    pad_bottom = "0" if last else "5px"
    return (
        "<tr><td style=\"padding:0 0 "
        f"{pad_bottom} 0;margin:0;border:0;mso-line-height-rule:exactly;"
        "line-height:20px;font-size:14px;"
        'font-family:Segoe UI,Arial,sans-serif;">'
        f"{tag_open}{content}{tag_close}</td></tr>"
    )


def _format_header_html(cto_norm: str, ubicacion: CtoUbicacion) -> str:
    dir_txt = escape(ubicacion.direccion or "—")
    maps_url = ubicacion.maps_url
    if maps_url:
        direccion = (
            f"<strong>Dirección:</strong> {dir_txt} "
            f'<a href="{escape(maps_url)}">Abrir en Maps</a>'
        )
    else:
        direccion = f"<strong>Dirección:</strong> {dir_txt}"

    if ubicacion.lat is not None and ubicacion.lon is not None:
        coord = f"<strong>Coordenadas:</strong> {ubicacion.lat}, {ubicacion.lon}"
    else:
        coord = "<strong>Coordenadas:</strong>"

    rows = [
        _header_row_html(f"<strong>Timbrado CTO — {escape(cto_norm)}</strong>"),
        _header_row_html("Fuente: inventario (FREE / RESERVED / IN SERVICE)"),
        _header_row_html(direccion),
        _header_row_html(coord),
        _header_row_html("NOC ATC — respuesta automática", em=True, last=True),
    ]
    return (
        '<table cellpadding="0" cellspacing="0" border="0" role="presentation" '
        'style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">'
        + "".join(rows)
        + "</table>"
    )


def build_timbrado_reply(
    cto: str,
    rows: list[CtoPortRow],
    *,
    ubicacion: CtoUbicacion | None = None,
) -> TimbradoReply:
    cto_norm, ubicacion = _resolve_ubicacion(cto, ubicacion)
    header = _format_header_lines(cto_norm, ubicacion)
    header_html = _format_header_html(cto_norm, ubicacion)

    if not rows:
        empty_msg = (
            f"Sin registros para {cto_norm} en inventario "
            f"(FREE / RESERVED / IN SERVICE).\n\n"
            "Verificá el identificador FATC o contactá a NOC."
        )
        sig_t = signature_text()
        sig_h = signature_html()
        return TimbradoReply(
            text="\n".join(header) + empty_msg + sig_t,
            html=(
                "<!DOCTYPE html><html><body "
                'style="font-family:Segoe UI,Arial,sans-serif;font-size:14px;">'
                f"{header_html}<p>{escape(empty_msg)}</p>{sig_h}</body></html>"
            ),
        )

    text = "\n".join(header + _format_ports_text(rows)) + "\n" + signature_text()
    html = (
        "<!DOCTYPE html><html><body "
        'style="font-family:Segoe UI,Arial,sans-serif;font-size:14px;">'
        f"{header_html}{_format_ports_html(rows)}{signature_html()}</body></html>"
    )
    return TimbradoReply(text=text, html=html)


def format_timbrado_reply(
    cto: str,
    rows: list[CtoPortRow],
    *,
    ubicacion: CtoUbicacion | None = None,
) -> str:
    return build_timbrado_reply(cto, rows, ubicacion=ubicacion).text
