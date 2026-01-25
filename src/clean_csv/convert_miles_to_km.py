from .config import MILES_RE
from .format_km import format_km


def convert_miles_to_km(text: str) -> str:
    def repl(match):
        start = float(match.group(1))
        end = float(match.group(2)) if match.group(2) else None
        if end is not None:
            start_km = format_km(start * 1.60934)
            end_km = format_km(end * 1.60934)
            return f"{start_km}-{end_km} km"
        return f"{format_km(start * 1.60934)} km"

    return MILES_RE.sub(repl, text)
