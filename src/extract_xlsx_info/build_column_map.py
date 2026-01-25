from typing import Dict, Any, List

from .config import DAYS
from .normalize_text import normalize_text


def build_column_map(header_row: List[Any]) -> Dict[str, int]:
    normalized = [normalize_text(v, add_km=False).lower() for v in header_row]
    col_map: Dict[str, int] = {}
    for key in ["week"] + [d.lower() for d in DAYS]:
        if key in normalized:
            col_map[key] = normalized.index(key)
    if "week" not in col_map:
        raise ValueError("Week column not found in header")
    return col_map
