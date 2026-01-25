from typing import List

from .config import DAY_PLACEHOLDER_RE, DAYS_RE, PUNCT_ONLY_RE


def is_row_invalid(row: List[str]) -> bool:
    if len(row) < 8:
        return True

    for cell in row[1:]:
        raw = cell.strip()
        if not raw:
            return True
        if DAYS_RE.search(raw) or DAY_PLACEHOLDER_RE.search(raw):
            return True
        if PUNCT_ONLY_RE.fullmatch(raw):
            return True

    return False
