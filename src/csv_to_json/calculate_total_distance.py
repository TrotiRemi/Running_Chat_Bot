import re


def calculate_total_distance(weeks):
    total_distance = 0.0
    for week in weeks:
        for training in week["days"].values():
            if training.lower() != "rest":
                distances = re.findall(
                    r"(\d+\.?\d*)\s*(km|kilometers|kilometres|miles|mile)",
                    training,
                    re.IGNORECASE,
                )
                for distance_str, unit in distances:
                    try:
                        distance = float(distance_str)
                        if unit.lower() in ["mile", "miles"]:
                            distance *= 1.609
                        total_distance += distance
                    except ValueError:
                        pass
    return round(total_distance, 1)
