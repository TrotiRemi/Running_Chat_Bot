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


def build_input_text_variations(features: dict, max_variants: int = 14):
    """Génère plusieurs variantes d'input pour couvrir des requêtes courtes/partielles.

    Objectif: enrichir le dataset pour des entrées comme:
    - "entrainement 10 km"
    - "entrainement beginner"
    - "marathon 20 semaines 5 séances"

    Retourne une liste d'objets {"label": str, "text": str}.
    """

    def _is_known(v):
        return v not in (None, "", "unknown", "Non précisé")

    goal_distance = features.get("goal_distance")
    level = features.get("level")
    weeks = features.get("weeks_training")
    sessions = features.get("training_per_week")
    goal_time = features.get("goal_time")

    def _display_goal(g):
        if not _is_known(g):
            return None
        s = str(g).strip()
        m = __import__("re").match(r"^(\d+(?:\.\d+)?)km$", s, flags=__import__("re").IGNORECASE)
        if m:
            return f"{m.group(1)} km"
        if s.lower() == "halfmarathon":
            return "semi-marathon"
        if s.lower() == "general fitness":
            return "remise en forme"
        return s

    def _level_variants(lvl):
        if not _is_known(lvl):
            return []
        lvl = str(lvl).strip().lower()
        mapping = {
            "beginner": ["beginner", "débutant"],
            "intermediate": ["intermediate", "intermédiaire"],
            "advanced": ["advanced", "avancé"],
            "maintenance": ["maintenance"],
            "general": ["general", "général"],
        }
        return mapping.get(lvl, [lvl])

    goal_disp = _display_goal(goal_distance)
    level_opts = _level_variants(level)

    def _add(items, label, text):
        t = (text or "").strip()
        if not t:
            return
        t = " ".join(t.split())
        items.append({"label": label, "text": t})

    items = []

    # 1) Version complète (format clé/valeur) = baseline
    _add(items, "full_kv", build_input_text(features))

    # 2) Phrases naturelles (plus proches du site)
    parts = []
    if goal_disp:
        parts.append(f"Objectif {goal_disp}")
    if level_opts:
        parts.append(f"niveau {level_opts[0]}")
    if _is_known(weeks):
        parts.append(f"{weeks} semaines")
    if _is_known(sessions):
        parts.append(f"{sessions} séances par semaine")
    if _is_known(goal_time):
        parts.append(f"objectif {goal_time}")
    if parts:
        _add(items, "natural_sentence", "Je veux un plan d'entraînement: " + ", ".join(parts) + ".")

    # 3) Requêtes ultra-courtes (les cas que tu cites)
    if goal_disp:
        _add(items, "short_goal", f"entrainement {goal_disp}")
        _add(items, "short_goal_plain", f"{goal_disp}")
        if goal_disp.lower().endswith(" km"):
            _add(items, "short_goal_10km_style", f"entrainement {goal_disp.replace(' ', '')}")

    for lvl in level_opts[:2]:
        _add(items, "short_level", f"entrainement {lvl}")
        _add(items, "short_level_plain", f"{lvl}")

    # 4) Combinaisons partielles
    if goal_disp and level_opts:
        _add(items, "goal_plus_level", f"entrainement {goal_disp} {level_opts[0]}")
        _add(items, "plan_goal_level", f"plan {goal_disp} niveau {level_opts[0]}")

    if goal_disp and _is_known(sessions):
        _add(items, "goal_plus_sessions", f"plan {goal_disp} {sessions} séances par semaine")

    if _is_known(sessions) and _is_known(weeks):
        _add(items, "sessions_plus_weeks", f"plan {weeks} semaines {sessions} séances")

    if goal_disp and _is_known(weeks):
        _add(items, "goal_plus_weeks", f"plan {goal_disp} {weeks} semaines")

    # Déduplication en gardant l'ordre
    seen = set()
    deduped = []
    for it in items:
        key = it["text"].lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)

    return deduped[:max_variants]
