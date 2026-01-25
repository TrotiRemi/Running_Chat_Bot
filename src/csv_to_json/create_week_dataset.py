from collections import defaultdict

from .augment_week_days import augment_week_days
from .build_input_text import build_input_text
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
            "version": "2.1",
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
            },
        },
        "training_data": [],
    }

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
            input_text = build_input_text(features)

            for instr_idx, instruction in enumerate(instruction_variations):
                dataset["training_data"].append(
                    {
                        "instruction": instruction,
                        "input": input_text,
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
