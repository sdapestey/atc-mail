"""Mapeo operator_id → nombre comercial (misma tabla que atc-noc-suite)."""
from __future__ import annotations

from typing import Any

OPERADORES = {
    1001: "TASA",
    3001: "DIRECTV",
    3950: "IPLAN",
    4000: "METROTEL",
    4010: "METROTEL",
    962: "SION",
    963: "SION",
    2800: "ATC",
    2805: "ATC",
    2806: "ATC",
}


def nombre_operador(op_id: Any) -> str:
    if op_id is None:
        return "—"
    try:
        return OPERADORES.get(int(op_id), str(op_id))
    except (TypeError, ValueError):
        return OPERADORES.get(op_id, str(op_id))
