import random
import re


def augment_week_days(week_data: dict) -> dict:
    """
    Reduce over-representation of Rest and ensure distances for Easy Run/Long Run.
    - If Rest days >= 4, convert some Rest to "X km Run" (5-10 km).
    - If Easy Run has no distance, add 5-10 km.
    - If Long Run has no distance, add 10-15 km.
    """
    if not week_data or "days" not in week_data:
        return week_data

    days = week_data["days"]
    rest_days = [k for k, v in days.items() if str(v).strip().lower() == "rest"]

    if len(rest_days) >= 4:
        convert_count = max(1, len(rest_days) - 3)
        random.shuffle(rest_days)
        for day_key in rest_days[:convert_count]:
            km = random.randint(5, 10)
            days[day_key] = f"{km} km Run"

    for day_key, val in list(days.items()):
        text = str(val).strip()
        if re.search(r"\beasy\s*run\b", text, re.IGNORECASE):
            has_distance = re.search(r"\d+\.?\d*\s*(km|kilometers|kilometres|miles|mile)", text, re.IGNORECASE)
            if not has_distance:
                km = random.randint(5, 10)
                days[day_key] = f"{km} km Easy Run"

        if re.search(r"\blong\s*run\b", text, re.IGNORECASE):
            has_distance = re.search(r"\d+\.?\d*\s*(km|kilometers|kilometres|miles|mile)", text, re.IGNORECASE)
            if not has_distance:
                km = random.randint(10, 15)
                days[day_key] = f"{km} km Long Run"

    week_data["days"] = days
    return week_data
