import re


def is_high_quality_week(week_data: dict, min_non_rest: int = 3) -> bool:
    if not week_data or "days" not in week_data:
        return False

    days = list(week_data["days"].values())
    non_rest = [d for d in days if str(d).strip().lower() != "rest"]
    if len(non_rest) < min_non_rest:
        return False

    joined = " ".join(non_rest).lower()
    has_distance = re.search(r"\d+\.?\d*\s*(km|kilometers|kilometres|miles|mile)", joined)
    has_keyword = any(k in joined for k in ["run", "long", "interval", "tempo", "recovery", "repetition"])
    return bool(has_distance or has_keyword)
