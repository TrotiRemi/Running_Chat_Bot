def calculate_training_days_per_week(weeks):
    if not weeks:
        return 0

    total_training_days = 0
    for week in weeks:
        training_days = 0
        for training in week["days"].values():
            if training.lower() != "rest":
                training_days += 1
        total_training_days += training_days

    return round(total_training_days / len(weeks))
