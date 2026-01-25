import re

from .config import K_DISTANCE_RE, MIN_RE, SEC_RE, TOKEN_REPLACEMENTS


def expand_abbreviations(text: str) -> str:
    def token_repl(match: re.Match) -> str:
        token = match.group(0)
        return TOKEN_REPLACEMENTS.get(token, token)

    text = re.sub(r"\b[A-Z]{2,}\b", token_repl, text)
    text = K_DISTANCE_RE.sub(lambda m: f"{m.group(1)} km", text)
    text = MIN_RE.sub("minutes", text)
    text = SEC_RE.sub("seconds", text)
    text = re.sub(r"\bZ(\d)\b", r"2\1", text)
    text = re.sub(r"\b(run)\s+run\b", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(tempo run)\s+run\b", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(long run)\s+run\b", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d(?!x)[A-Za-z]\b|\b[A-Za-z](?!x)\d\b", "", text)
    text = re.sub(r"\b([A-Z])\b", "", text)
    text = re.sub(r"(?<=\s)[\.,;:!\-]+(?=\s)", " ", text)
    return text
