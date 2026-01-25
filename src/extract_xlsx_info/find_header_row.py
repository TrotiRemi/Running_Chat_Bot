from typing import List, Any

from .normalize_text import normalize_text


def find_header_row(rows: List[List[Any]]) -> int:
    for idx, row in enumerate(rows):
        normalized = [normalize_text(v, add_km=False).lower() for v in row]
        if "week" in normalized and "monday" in normalized:
            return idx
    raise ValueError("Header row with Week/Monday not found")
