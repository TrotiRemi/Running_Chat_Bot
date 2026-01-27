from collections import defaultdict
import random
import re

from .augment_week_days import augment_week_days
from .build_input_text import build_input_text_variations
from .calculate_avg_distance_per_run import calculate_avg_distance_per_run
from .calculate_total_distance import calculate_total_distance
from .calculate_training_days_per_week import calculate_training_days_per_week
from .config import INPUT_DIRS, DAYS_FR
from .extract_features_from_filename import extract_features_from_filename
from .format_week_output import format_week_output
from .generate_instruction_variations import generate_instruction_variations
from .is_high_quality_week import is_high_quality_week
from .parse_csv_file import parse_csv_file


def create_week_dataset(augmentation_factor=2):
    dataset = {
        "metadata": {
            "project": "Running Weekly Training Schedule Prediction",
            "description": "Optimized & augmented dataset for week prediction",
            "version": "2.6",
            "augmentation_factor": augmentation_factor,
            "total_training_pairs": 0,
            "statistics": {
                "by_level": defaultdict(int),
                "by_goal": defaultdict(int),
                "by_training_days": defaultdict(int),
                "by_duration": defaultdict(int),
                "ocr_corrections": 0,
            },
            "data_quality": {
                "complete_weeks": 0,
                "avg_distance_total": 0,
                "unique_programs": 0,
                "cleaned_entries": 0,
                "dropped_basic_weeks": 0,
                "kept_basic_weeks": 0,
            },
        },
        "training_data": [],
    }

    # Downsample ultra-basic weeks (mostly Run/Rest) to avoid the model collapsing to
    # short repetitive runs. Keep a few per program, then probabilistically drop the rest.
    RNG_SEED = 42
    random.seed(RNG_SEED)

    BASIC_WEEK_KEEP_PROB = 0.35
    MIN_BASIC_WEEKS_PER_PROGRAM = 2

    distance_re = re.compile(r"(\d+(?:\.\d+)?)\s*(km|kilometers|kilometres|miles|mile)", re.IGNORECASE)

    def _week_tags_and_max_km(week_data: dict):
        tags = set()
        max_km = 0.0
        days = (week_data or {}).get("days") or {}

        for training in days.values():
            t = str(training or "").strip()
            lower = t.lower()

            if lower == "rest":
                tags.add("rest")
            if "long run" in lower:
                tags.add("long")
            if any(k in lower for k in ["interval", "repeats", "repetition", "répétition", "track"]):
                tags.add("interval")
            if "tempo" in lower:
                tags.add("tempo")
            if any(k in lower for k in ["marathon pace", "threshold"]):
                tags.add("pace")
            if "cross" in lower:
                tags.add("cross")
            if "stride" in lower:
                tags.add("strides")
            if "recovery" in lower:
                tags.add("recovery")
            if "run" in lower:
                tags.add("run")

            for d_str, unit in distance_re.findall(t):
                try:
                    d = float(d_str)
                except ValueError:
                    continue
                if unit.lower() in {"mile", "miles"}:
                    d *= 1.609
                max_km = max(max_km, d)

        return tags, max_km

    def _is_basic_week(week_data: dict) -> bool:
        tags, max_km = _week_tags_and_max_km(week_data)
        # Basic if it contains no long/quality/cross elements and distances are short-ish.
        has_quality = any(t in tags for t in {"interval", "tempo", "pace", "strides", "cross"})
        has_long = "long" in tags
        if has_quality or has_long:
            return False
        # If we only see Run/Rest/Recovery, treat as basic.
        allowed = {"run", "rest", "recovery"}
        if not tags.issubset(allowed):
            return False
        # Very small runs tend to dominate; downsample those.
        return max_km <= 12.0

    csv_files = []
    for input_dir in INPUT_DIRS:
        if input_dir.exists():
            csv_files.extend(sorted(input_dir.glob("*.csv")))

    print(f"📁 Trouvé {len(csv_files)} fichiers CSV")
    print(f"🔄 Facteur d'augmentation: {augmentation_factor}x\n")

    all_distances = []

    for csv_file in csv_files:
        filename = csv_file.name
        features = extract_features_from_filename(filename)

        # Track whether the goal time was explicitly present (filename-derived).
        # We only use this signal for level heuristics; inferred defaults shouldn't upgrade levels.
        goal_time_from_filename = bool(features.get("goal_time"))

        weeks = parse_csv_file(csv_file)
        if not weeks:
            continue

        filtered_weeks = [w for w in weeks if is_high_quality_week(w, min_non_rest=3)]
        if not filtered_weeks:
            continue

        training_days_per_week = calculate_training_days_per_week(filtered_weeks)
        total_distance = calculate_total_distance(filtered_weeks)
        avg_distance_per_run = calculate_avg_distance_per_run(filtered_weeks)
        num_weeks = len(filtered_weeks)

        if not features["training_per_week"]:
            features["training_per_week"] = training_days_per_week
        if not features["weeks_training"]:
            features["weeks_training"] = num_weeks
        if not features["goal_distance"]:
            features["goal_distance"] = "general fitness"

        def _parse_goal_time_to_minutes(time_str: str | None):
            if not time_str:
                return None
            s = str(time_str).strip().lower().replace(" ", "")
            # Accept forms like: 3h30m, 3h30, 3h, 55m, 1h50
            m = re.fullmatch(r"(?:(\d+)h)?(?:(\d{1,2})m?)?", s)
            if not m:
                return None
            hours = int(m.group(1) or 0)
            minutes = int(m.group(2) or 0)
            total = hours * 60 + minutes
            return total if total > 0 else None

        # Level heuristics requested by user
        goal_norm = str(features.get("goal_distance") or "").strip().lower()
        level_norm = str(features.get("level") or "").strip().lower()
        time_minutes = _parse_goal_time_to_minutes(features.get("goal_time"))

        if goal_norm in {"marathon", "halfmarathon"}:
            # Default: intermediate for marathon/halfmarathon
            features["level"] = "intermediate"
            # Exception: marathon with explicitly-specified time < 3h30 => advanced
            if goal_norm == "marathon" and goal_time_from_filename and time_minutes is not None and time_minutes < 210:
                features["level"] = "advanced"

        # If 5k/10k without an explicit goal time, treat as beginner
        if goal_norm in {"5km", "10km"} and not goal_time_from_filename:
            features["level"] = "beginner"

        if not features.get("goal_time"):
            goal = features.get("goal_distance")
            level = features.get("level")
            goal_time_map = {
                "marathon": {
                    "advanced": "3h30m",
                    "intermediate": "4h30m",
                    "beginner": "5h30m",
                },
                "halfmarathon": {
                    "advanced": "1h40m",
                    "intermediate": "2h",
                    "beginner": "2h30m",
                },
                "10km": {
                    "advanced": "40m",
                    "intermediate": "55m",
                    "beginner": "1h30m",
                },
                "5km": {
                    "advanced": "20m",
                    "intermediate": "25m",
                    "beginner": "35m",
                },
            }
            if goal in goal_time_map and level in goal_time_map[goal]:
                features["goal_time"] = goal_time_map[goal][level]

        all_distances.append(total_distance)

        kept_basic_for_program = 0

        for week_data in filtered_weeks:
            week_num = week_data["week"]

            week_data = augment_week_days(week_data)

            instruction_variations = generate_instruction_variations(
                week_num,
                features["weeks_training"],
                features["goal_distance"],
                features["level"],
                features["training_per_week"],
                features["age"],
            )

            output = format_week_output(week_data)
            input_variations = build_input_text_variations(features)

            # Downsample overly-basic weeks after augmentation step.
            # We keep a small baseline per program so "simple" cases still exist.
            if _is_basic_week(week_data):
                if kept_basic_for_program < MIN_BASIC_WEEKS_PER_PROGRAM:
                    kept_basic_for_program += 1
                    dataset["metadata"]["data_quality"]["kept_basic_weeks"] += 1
                else:
                    if random.random() > BASIC_WEEK_KEEP_PROB:
                        dataset["metadata"]["data_quality"]["dropped_basic_weeks"] += 1
                        continue
                    kept_basic_for_program += 1
                    dataset["metadata"]["data_quality"]["kept_basic_weeks"] += 1

            for input_idx, input_var in enumerate(input_variations):
                for instr_idx, instruction in enumerate(instruction_variations):
                    dataset["training_data"].append(
                        {
                            "instruction": instruction,
                            "input": input_var["text"],
                            "output": output,
                            "metadata": {
                                "program": filename.replace(".csv", ""),
                                "week": week_num,
                                "total_weeks": features["weeks_training"],
                                "training_days": features["training_per_week"],
                                "goal": features["goal_distance"],
                                "level": features["level"],
                                "program_total_distance": total_distance,
                                "avg_distance_per_run": avg_distance_per_run,
                                "augmentation_variant": instr_idx + 1,
                                "input_variant": input_idx + 1,
                                "input_variant_label": input_var.get("label"),
                                "is_complete_week": all(
                                    week_data["days"].get(day.lower(), "Rest").lower() != "rest"
                                    for day in DAYS_FR[: features["training_per_week"]]
                                ),
                            },
                        }
                    )

                    dataset["metadata"]["total_training_pairs"] += 1
                    dataset["metadata"]["statistics"]["by_level"][features["level"]] += 1
                    dataset["metadata"]["statistics"]["by_goal"][features["goal_distance"]] += 1
                    dataset["metadata"]["statistics"]["by_training_days"][features["training_per_week"]] += 1
                    dataset["metadata"]["statistics"]["by_duration"][features["weeks_training"]] += 1

        dataset["metadata"]["data_quality"]["complete_weeks"] += num_weeks
        dataset["metadata"]["data_quality"]["unique_programs"] += 1

        print(
            f"✓ {filename}\n"
            f"  └─ {num_weeks}w | {features['goal_distance']} | {features['level']} | "
            f"{features['training_per_week']}j/sem | ×{augmentation_factor} = {num_weeks * augmentation_factor} pairs"
        )

    if all_distances:
        dataset["metadata"]["data_quality"]["avg_distance_total"] = round(
            sum(all_distances) / len(all_distances),
            1,
        )

    return dataset
