import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Any, List


class DatasetValidator:
    """Validate CSV data quality."""

    VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    ACTIVITY_KEYWORDS = {
        "easy_run": ["easy", "run", "light"],
        "long_run": ["long", "lsd", "distance"],
        "tempo": ["tempo", "threshold"],
        "interval": ["interval", "repeat", "track", "400m", "800m", "1k", "1m"],
        "hill": ["hill", "uphill", "downhill"],
        "speed": ["speed", "fast", "pace"],
        "fartlek": ["fartlek", "speed play"],
        "cross_train": ["cross-train", "cross train", "swim", "bike", "cycle", "elliptical"],
        "rest": ["rest", "recovery", "off"],
    }

    @staticmethod
    def validate_week(week_data: Dict[str, str]) -> Dict[str, Any]:
        issues: List[str] = []
        if "Week" not in week_data:
            issues.append("Missing 'Week' field")

        rest_count = 0
        training_count = 0
        corrupted_count = 0

        for day in DatasetValidator.VALID_DAYS:
            if day not in week_data:
                issues.append(f"Missing day: {day}")
                continue

            activity = (week_data[day] or "").strip()
            if activity.lower() == "rest":
                rest_count += 1
            elif len(activity) < 2 or activity == "." * len(activity):
                corrupted_count += 1
                issues.append(f"{day}: Corrupted activity: '{activity}'")
            else:
                training_count += 1

        if corrupted_count > 0:
            issues.append(f"Contains {corrupted_count} corrupted entries")
        if rest_count == 7:
            issues.append("Week has 0 training days")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "rest_days": rest_count,
            "training_days": training_count,
            "corrupted_entries": corrupted_count,
        }

    @staticmethod
    def categorize_activity(activity: str) -> str:
        if activity.lower() == "rest":
            return "rest"
        activity_lower = activity.lower()
        for category, keywords in DatasetValidator.ACTIVITY_KEYWORDS.items():
            if any(keyword in activity_lower for keyword in keywords):
                return category
        return "other"

    @staticmethod
    def analyze_csv(csv_path: Path) -> Dict[str, Any] | None:
        stats: Dict[str, Any] = {
            "file": csv_path.name,
            "total_weeks": 0,
            "valid_weeks": 0,
            "weeks_with_issues": [],
            "activity_types": Counter(),
            "avg_activity_length": [],
            "unique_activities": set(),
            "rest_days_distribution": [],
            "training_days_distribution": [],
            "corrupted_weeks": 0,
            "issues": defaultdict(int),
        }

        try:
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    stats["total_weeks"] += 1

                    validation = DatasetValidator.validate_week(row)
                    if validation["is_valid"]:
                        stats["valid_weeks"] += 1
                    else:
                        stats["corrupted_weeks"] += 1
                        stats["weeks_with_issues"].append(
                            {"week_num": row_num, "issues": validation["issues"]}
                        )
                        for issue in validation["issues"]:
                            stats["issues"][issue] += 1

                    stats["rest_days_distribution"].append(validation["rest_days"])
                    stats["training_days_distribution"].append(validation["training_days"])

                    for day in DatasetValidator.VALID_DAYS:
                        activity = (row.get(day) or "").strip()
                        if activity:
                            category = DatasetValidator.categorize_activity(activity)
                            stats["activity_types"][category] += 1
                            stats["unique_activities"].add(activity)
                            stats["avg_activity_length"].append(len(activity))
        except Exception as exc:
            print(f"❌ Error reading {csv_path}: {exc}")
            return None

        stats["avg_activity_length"] = (
            sum(stats["avg_activity_length"]) / len(stats["avg_activity_length"])
            if stats["avg_activity_length"]
            else 0
        )
        stats["avg_rest_days"] = (
            sum(stats["rest_days_distribution"]) / len(stats["rest_days_distribution"])
            if stats["rest_days_distribution"]
            else 0
        )
        stats["avg_training_days"] = (
            sum(stats["training_days_distribution"]) / len(stats["training_days_distribution"])
            if stats["training_days_distribution"]
            else 0
        )
        stats["unique_activities_count"] = len(stats["unique_activities"])

        return stats
