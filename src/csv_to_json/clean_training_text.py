import re


def clean_training_text(text: str) -> str:
    if not text:
        return "Rest"

    text = str(text).strip()

    text = re.sub(r"m\s+iles", "miles", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkm\s*\.", "km", text, flags=re.IGNORECASE)

    def _normalize_range_two_units(match):
        start = match.group(1)
        unit1 = match.group(2)
        end = match.group(3)
        unit = unit1 or match.group(4) or "km"
        unit = "km" if unit.lower() in ["km", "kilometers", "kilometres"] else "mile"
        return f"{start}-{end} {unit}"

    def _normalize_range_single_unit(match):
        start = match.group(1)
        end = match.group(2)
        unit = match.group(3)
        unit = "km" if unit.lower() in ["km", "kilometers", "kilometres"] else "mile"
        return f"{start}-{end} {unit}"

    text = re.sub(
        r"(\d+\.?\d*)\s*(km|kilometers|kilometres|miles|mile)\s*[-–]\s*"
        r"(\d+\.?\d*)\s*(km|kilometers|kilometres|miles|mile)",
        _normalize_range_two_units,
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\s*(km|kilometers|kilometres|miles|mile)",
        _normalize_range_single_unit,
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"(\d+)\s*[-–]\s*(\d+)\s*minutes?\b",
        r"\1 à \2 minutes",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"(\d+)\s*[-–]\s*(\d+)\s*(reps?|repetitions?|répétitions?|repeat|fois)\b",
        r"\1 à \2 fois",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"(reps?|repetitions?|répétitions?|repeat)\s*(\d+)\s*[-–]\s*(\d+)",
        r"\2 à \3 fois",
        text,
        flags=re.IGNORECASE,
    )

    if re.fullmatch(r"(?i)(rest|rest day|day off|off)", text):
        return "Rest"

    replacements = {
        r"\bQuality Day\b": "Easy Run",
        r"\bFlex Day\b": "Easy Run",
        r"\bCross Training\b": "Cross-Train",
        r"\bCross-?Train\b": "Cross-Train",
        r"\bLong Slow Distance\b": "Long Run",
        r"\bMarathon Pace\b": "Marathon Pace",
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    text = re.sub(r"\bDay Off\b", "Rest", text, flags=re.IGNORECASE)
    text = re.sub(r"\bwith\b", "", text, flags=re.IGNORECASE)

    garbage_phrases = [
        r"\bat speed\b",
        r"\bat lactate\b",
        r"\bThreshold\b",
        r"\bTempo\b",
        r"\bFartlek\b",
        r"\bTrack\b",
        r"\btraining\b",
        r"\bworkout\b",
        r"\bwalk\b",
        r"\bbrisk\b",
        r"\bmagic\b",
        r"\bHills\b",
        r"\bhill\b",
        r"\buphill\b",
        r"\buphills\b",
        r"\bgoal\b",
        r"\brehearsal\b",
        r"\bglute\b",
        r"\bstabilit\w*\b",
        r"\bleg\b",
        r"\bstrength\b",
        r"\bthen\b",
        r"\bdown\b",
        r"\bup\b",
        r"\bback\b",
        r"\bstart\b",
        r"\bpoint\b",
        r"\btotal\b",
        r"\bxt\b",
    ]
    for pattern in garbage_phrases:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text).strip()

    text = re.sub(r"\b(and|et)\b\s*$", "", text, flags=re.IGNORECASE).strip()

    distance_match = re.search(
        r"(\d+\.?\d*(?:-\d+\.?\d*)?\s*(?:km|kilometers|kilometres|miles|mile))",
        text,
        flags=re.IGNORECASE,
    )
    if distance_match:
        distance_text = distance_match.group(1).lower()
        distance_text = distance_text.replace("kilometers", "km").replace("kilometres", "km")
        distance_text = distance_text.replace("miles", "mile")

        activity = None
        if re.search(r"\blong\s*run\b", text, re.IGNORECASE):
            activity = "Long Run"
        elif re.search(r"\beasy\s*run\b", text, re.IGNORECASE):
            activity = "Easy Run"
        elif re.search(r"\bintervals?\b", text, re.IGNORECASE):
            activity = "Intervals"
        elif re.search(r"\bmarathon\s*pace\b", text, re.IGNORECASE):
            activity = "Marathon Pace"
        elif re.search(r"\btempo\b", text, re.IGNORECASE):
            activity = "Tempo Run"
        elif re.search(r"\brecovery\b", text, re.IGNORECASE):
            activity = "Recovery Run"
        elif re.search(r"\bcross-?train\b", text, re.IGNORECASE):
            activity = "Cross-Train"
        elif re.search(r"\brun\b", text, re.IGNORECASE):
            activity = "Run"

        if activity:
            text = f"{distance_text} {activity}"
        else:
            text = distance_text

    keywords = ["easy", "run", "long", "recovery"]
    has_distance = re.search(r"\d+\.?\d*\s*(km|kilometers|kilometres|miles|mile)", text, re.IGNORECASE)
    has_keyword = any(k in text.lower() for k in keywords)
    if not has_distance and not has_keyword:
        return "Rest"

    if not text or len(text) < 2:
        return "Rest"

    return text
