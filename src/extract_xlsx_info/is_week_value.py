from typing import Any

from .normalize_text import normalize_text


def is_week_value(value: Any) -> bool:
    text = normalize_text(value, add_km=False)
    if not text:
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False
