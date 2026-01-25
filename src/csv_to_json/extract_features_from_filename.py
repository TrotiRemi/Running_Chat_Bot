import re


def extract_features_from_filename(filename: str):
    features = {
        "goal_distance": None,
        "goal_time": None,
        "level": None,
        "weeks_training": None,
        "training_per_week": None,
        "age": None,
    }

    name = filename.lower()
    name_clean = re.sub(r"\.(csv|pdf|xlsx)$", "", name)
    name_clean = re.sub(r"run\s*walk\s*", "", name_clean)

    distance_match = re.search(r"(\d+)\s*(k|km|mile|miles)(?![a-z])", name_clean)
    if distance_match:
        value = int(distance_match.group(1))
        unit = distance_match.group(2)
        if unit in ["mile", "miles"]:
            km = round(value * 1.609, 1)
            features["goal_distance"] = f"{km}km"
        else:
            features["goal_distance"] = f"{value}km"
    elif "halfmarathon" in name_clean or "half-marathon" in name_clean:
        features["goal_distance"] = "halfmarathon"
    elif "marathon" in name_clean:
        features["goal_distance"] = "marathon"

    if "beginner" in name_clean:
        features["level"] = "beginner"
    elif "intermediate" in name_clean:
        features["level"] = "intermediate"
    elif "advanced" in name_clean:
        features["level"] = "advanced"
    elif "maintenance" in name_clean:
        features["level"] = "maintenance"
    else:
        features["level"] = "general"

    weeks_match = re.search(r"(\d+)w", name_clean)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        if 1 <= weeks <= 100:
            features["weeks_training"] = weeks

    training_match = re.search(r"(\d{1,2})d", name_clean)
    if training_match:
        training = int(training_match.group(1))
        if 1 <= training <= 7:
            features["training_per_week"] = training

    time_match = re.search(r"(\d+)h(\d{1,2})", name_clean)
    if time_match:
        features["goal_time"] = f"{time_match.group(1)}h{time_match.group(2)}m"
    else:
        time_match = re.search(r"(\d+)h(?![\d])", name_clean)
        if time_match:
            features["goal_time"] = f"{time_match.group(1)}h"

    age_match = re.search(r"(?:^|[-_])(\d{2})(?:[-_]|$)", name_clean)
    if age_match:
        age = int(age_match.group(1))
        if 20 <= age <= 80:
            features["age"] = age

    return features
