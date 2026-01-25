import re


def add_km_to_numbers(text: str) -> str:
    def repl(match: re.Match) -> str:
        number = match.group(1)
        return f"{number}km"

    return re.sub(
        r"\b(\d+\.\d+)\b(?!\s*km)(?!\s*minutes)(?!\s*mins)(?!\s*min)",
        repl,
        text,
    )
