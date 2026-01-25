from typing import Dict

from .activity_cleaner import ActivityCleaner


class WeekValidator:
    """Validate and complete week structures."""

    DAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @staticmethod
    def complete_week(week_data: Dict[str, str], week_num: int) -> Dict[str, str]:
        completed = {"Week": week_num}
        for day_label in WeekValidator.DAY_LABELS:
            activity = week_data.get(day_label, "").strip()
            if activity:
                activity = ActivityCleaner.clean_single_activity(activity)
            else:
                activity = "Rest"
            completed[day_label] = activity
        return completed

    @staticmethod
    def validate_week(week_data: Dict[str, str]) -> bool:
        training_days = sum(
            1 for day in WeekValidator.DAY_LABELS if week_data.get(day, "").lower() != "rest"
        )
        return training_days > 0
