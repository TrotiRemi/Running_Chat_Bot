import re
from typing import Any


class ActivityCleaner:
    """Clean and validate workout activities."""

    INVALID_PATTERNS = [
        r"^\s*\.+\s*$",
        r"^\s*[=-]{2,}\s*$",
        r"^[A-Z]{1,2}\s*\d+$",
        r"^DAV\d+",
        r"^\d+\s*Rest$",
    ]

    REST_KEYWORDS = ["rest", "day off", "off day", "recovery", "cross-train", "cross train"]

    @staticmethod
    def is_rest_activity(activity: str) -> bool:
        activity_lower = activity.lower().strip()
        if activity_lower in ["rest", ""]:
            return True
        return any(keyword in activity_lower for keyword in ActivityCleaner.REST_KEYWORDS)

    @staticmethod
    def clean_single_activity(activity: Any) -> str:
        if not activity:
            return "Rest"
        activity = str(activity).strip()
        for pattern in ActivityCleaner.INVALID_PATTERNS:
            if re.match(pattern, activity, re.IGNORECASE):
                return "Rest"
        activity = re.sub(r"\s+", " ", activity).strip()
        if len(activity) < 2:
            return "Rest"
        if ActivityCleaner.is_rest_activity(activity):
            return "Rest"
        return activity

    @staticmethod
    def merge_multiline_activity(cell_content: Any) -> str:
        if not cell_content:
            return ""
        lines = str(cell_content).split("\n")
        cleaned_lines = []
        for line in lines:
            line = ActivityCleaner.clean_single_activity(line)
            if line != "Rest":
                cleaned_lines.append(line)
        if not cleaned_lines:
            return "Rest"
        return " | ".join(cleaned_lines)
