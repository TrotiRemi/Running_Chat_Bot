def build_input_text(features: dict) -> str:
    def fmt(value, label):
        return value if value not in (None, "", "unknown") else "Non précisé"

    goal_distance = fmt(features.get("goal_distance"), "Objectif")
    level = fmt(features.get("level"), "Niveau")
    weeks = fmt(features.get("weeks_training"), "Semaines")
    sessions = fmt(features.get("training_per_week"), "Séances/sem")
    goal_time = fmt(features.get("goal_time"), "Temps objectif")

    return (
        f"Objectif: {goal_distance}; "
        f"Niveau: {level}; "
        f"Semaines: {weeks}; "
        f"Séances/sem: {sessions}; "
        f"Temps objectif: {goal_time}."
    )
