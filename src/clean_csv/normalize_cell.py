import re

from .config import DISALLOWED_CHARS_RE, OCR_REPLACEMENTS
from .convert_miles_to_km import convert_miles_to_km
from .expand_abbreviations import expand_abbreviations


def normalize_cell(value: str) -> str:
    cell = value.replace("\u00a0", " ").replace("■", " ")
    cell = cell.replace("|", " ")
    cell = DISALLOWED_CHARS_RE.sub(" ", cell)
    cell = cell.replace("(", " ").replace(")", " ").replace("!", " ")
    cell = re.sub(r"\s+", " ", cell).strip()

    if re.fullmatch(r"(?i)(rest|off|day\s*off)", cell):
        return "Day Off"

    for pattern, replacement in OCR_REPLACEMENTS:
        cell = pattern.sub(replacement, cell)

    cell = re.sub(r"(?i)\bfull-body\s+weight\b", "Full-Body Body-Weight", cell)
    cell = expand_abbreviations(cell)
    cell = convert_miles_to_km(cell)
    cell = re.sub(r"\s+", " ", cell).strip()
    cell = re.sub(r"[\.,;:]+$", "", cell)

    return cell
