def get_day_value(row: dict, day_fr: str, day_en: str) -> str:
    for key in (day_fr, day_fr.lower(), day_en, day_en.lower()):
        if key in row and row[key] is not None:
            return str(row[key]).strip()
    return ""
