import hashlib
import re


def clean_training_text(text: str) -> str:
    if not text:
        return "Rest"

    raw_text = str(text).strip()
    text = raw_text

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
        r"\bQuality Day\b": "Run",
        r"\bFlex Day\b": "Run",
        r"\bCross Training\b": "Cross-Train",
        r"\bCross-?Train\b": "Cross-Train",
        r"\bLong Slow Distance\b": "Long Run",
        r"\bMarathon Pace\b": "Marathon Pace",
        # Unify synonyms / give consistent meaning
        # - Threshold ~= Tempo (sustained effort around lactate threshold)
        r"\bThreshold\b": "Tempo",
        # - Track / Fartlek are interval-like sessions
        r"\bTrack\b": "Intervals",
        r"\bFartlek\b": "Intervals",
        # - Hills / Uphill are hill sessions
        r"\bUphills?\b": "Hills",
        r"\bUp\s*hill\b": "Hills",
        r"\bHills?\b": "Hills",
        # - Strides are short accelerations
        r"\bStrides?\b": "Strides",
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    text = re.sub(r"\bDay Off\b", "Rest", text, flags=re.IGNORECASE)
    text = re.sub(r"\bwith\b", "", text, flags=re.IGNORECASE)

    garbage_phrases = [
        r"\bat speed\b",
        r"\bat lactate\b",
        r"\btraining\b",
        r"\bworkout\b",
        r"\bwalk\b",
        r"\bbrisk\b",
        r"\bmagic\b",
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

    # Canonicalize workout type labels (even when distance is missing)
    # Goal: reduce label noise and keep diversity terms with consistent meaning.
    canonical_patterns = [
        (r"\blong\s*run\b", "Long Run"),
        (r"\bmarathon\s*pace\b", "Marathon Pace"),
        (r"\btempo\b|\bthreshold\b", "Tempo Run"),
        (r"\bintervals?\b|\brepeats?\b|\brepetition\b|\brépétition\b|\btrack\b|\bfartlek\b", "Intervals"),
        (r"\bhills?\b|\buphill\b|\buphills\b", "Hills"),
        (r"\bstrides?\b", "Strides"),
        (r"\bcross-?train\b|\bcross\s*training\b", "Cross-Train"),
        (r"\brecovery\b", "Recovery Run"),
        (r"\brun\b", "Run"),
    ]

    canonical_activity = None
    for pat, label in canonical_patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            canonical_activity = label
            break

    def _stable_choice(options: list[float], seed_text: str) -> float:
        # Python's built-in hash is randomized across processes; use md5 for stability.
        digest = hashlib.md5(seed_text.encode("utf-8", errors="ignore")).hexdigest()
        idx = int(digest[:8], 16) % len(options)
        return options[idx]

    def _extract_quality_details(src: str) -> str | None:
        s = (src or "").strip()
        if not s:
            return None

        # Prefer rep-style patterns like 6x400m, 10 x 1km, 8×200m
        m = re.search(r"\b\d+\s*[x×]\s*\d+\s*(?:m|km|mile|mi)\b", s, flags=re.IGNORECASE)
        if m:
            return re.sub(r"\s+", "", m.group(0)).replace("×", "x")

        # Time patterns like 20 min, 30 minutes, 10 à 15 minutes
        m = re.search(r"\b\d+\s*(?:à\s*\d+\s*)?minutes?\b", s, flags=re.IGNORECASE)
        if m:
            return re.sub(r"\s+", " ", m.group(0)).strip()

        # Short distance hints if present without explicit 'km/mi' at start
        m = re.search(r"\b\d+(?:[\.,]\d+)?\s*(?:km|mile|mi)\b", s, flags=re.IGNORECASE)
        if m:
            return re.sub(r"\s+", " ", m.group(0)).strip().lower().replace("mi", "mile")

        return None

    distance_match = re.search(
        r"(\d+\.?\d*(?:-\d+\.?\d*)?\s*(?:km|kilometers|kilometres|miles|mile))",
        text,
        flags=re.IGNORECASE,
    )
    if distance_match:
        distance_text = distance_match.group(1).lower()
        distance_text = distance_text.replace("kilometers", "km").replace("kilometres", "km")
        distance_text = distance_text.replace("miles", "mile")

        activity = canonical_activity

        if activity:
            text = f"{distance_text} {activity}"
        else:
            text = distance_text
    else:
        # If no distance but we can identify an activity, keep the activity (don't collapse to Rest)
        if canonical_activity is not None:
            # Keep meaningful details for quality sessions when available; otherwise, add a
            # small default distance to avoid overly vague lines like "Intervals".
            if canonical_activity in {"Intervals", "Tempo Run", "Hills", "Strides"}:
                details = _extract_quality_details(raw_text)
                default_km_options = {
                    "Intervals": [5, 6, 7, 8],
                    "Tempo Run": [6, 8, 10, 12],
                    "Hills": [6, 7, 8, 10],
                    "Strides": [5, 6, 7, 8],
                }
                km = _stable_choice(default_km_options[canonical_activity], raw_text)
                km_text = str(int(km) if float(km).is_integer() else km)
                # Always include a distance prefix so the model learns a stable format.
                text = f"{km_text} km {canonical_activity}"
                if details:
                    text = f"{text} ({details})"
            else:
                text = canonical_activity

    # Keywords that should prevent the line from being collapsed to Rest
    keywords = [
        "easy",
        "run",
        "long",
        "recovery",
        "interval",
        "tempo",
        "marathon pace",
        "threshold",
        "hills",
        "hill",
        "strides",
        "cross",
    ]
    has_distance = re.search(r"\d+\.?\d*\s*(km|kilometers|kilometres|miles|mile)", text, re.IGNORECASE)
    has_keyword = any(k in text.lower() for k in keywords)
    if not has_distance and not has_keyword:
        return "Rest"

    if not text or len(text) < 2:
        return "Rest"

    # Final normalization: prefer 'Run' over 'Easy Run' everywhere, but keep 'Long Run'
    text = re.sub(r"\bEasy\s+Run\b", "Run", text, flags=re.IGNORECASE)
    return text
