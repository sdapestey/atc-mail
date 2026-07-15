"""Site / partido a partir del prefijo del identificador CTO."""
from __future__ import annotations

import re

# Prefijo alfabético del CTO (antes de los dígitos), ej. SI01 → SI
_CTO_PREFIX_RE = re.compile(r"^([A-Za-z]+)")

# Prefijos usados en FATC (misma lógica que nombres de partido en inventario)
_SITE_BY_PREFIX: dict[str, str] = {
    "SI": "San Isidro",
    "SF": "San Fernando",
    "ES": "Escobar",
    "TG": "Tigre",
    "MO": "Moreno",
    "VL": "Vicente Lopez",
    "SM": "San Martin",
}


def site_from_cto(cto: str | None) -> str:
    """
    Deriva el sitio desde el código CTO.

    Ejemplos:
      SI01-FATC-8-101093 → San Isidro
      TG01-FATC-8-109725 → Tigre
    """
    cto_norm = (cto or "").strip().upper()
    if not cto_norm:
        return ""
    head = cto_norm.split("-", 1)[0]
    m = _CTO_PREFIX_RE.match(head)
    if not m:
        return ""
    return _SITE_BY_PREFIX.get(m.group(1).upper(), "")
