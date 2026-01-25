from .config import DAYS_FR


def format_week_output(week_data):
    lines = []
    for day in DAYS_FR:
        training = week_data["days"].get(day.lower(), "Rest")
        lines.append(f"{day}: {training}")
    return "\n".join(lines)
