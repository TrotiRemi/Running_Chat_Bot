import re
from typing import Any

from .add_km_to_numbers import add_km_to_numbers


def normalize_text(value: Any, *, add_km: bool = True) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    text = re.sub(r"\bRPE\b", "repetition", text, flags=re.IGNORECASE)
    text = re.sub(r"\bRest Day\b", "Day Off", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\d+)\s*k\b", r"\1 km", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    if add_km:
        text = add_km_to_numbers(text)
    return text
