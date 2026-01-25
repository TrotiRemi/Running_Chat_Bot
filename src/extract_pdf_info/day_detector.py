import re
from typing import List, Optional

from .header_cleaner import HeaderCleaner


class DayDetector:
    """Detect and map day columns (named or numbered)."""

    DAY_NAMES_EN = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    DAY_NAMES_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    DAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @staticmethod
    def detect_format(headers: List[str]) -> str:
        named_count = 0
        numbered_count = 0
        for header in headers:
            if not header:
                continue
            header_lower = HeaderCleaner.clean(header).lower()
            if any(day in header_lower for day in DayDetector.DAY_NAMES_EN + DayDetector.DAY_NAMES_FR):
                named_count += 1
            if re.match(r"day\s*\d+", header_lower) or re.match(r"day\d+", header_lower):
                numbered_count += 1
        if named_count >= numbered_count and named_count > 0:
            return "named"
        if numbered_count > named_count:
            return "numbered"
        return "unknown"

    @staticmethod
    def extract_day_number(header_text: str) -> Optional[int]:
        match = re.search(r"day\s*(\d+)", header_text.lower())
        return int(match.group(1)) if match else None

    @staticmethod
    def extract_day_name(header_text: str) -> Optional[str]:
        header_lower = HeaderCleaner.clean(header_text).lower()
        for i, day in enumerate(DayDetector.DAY_NAMES_EN):
            if day in header_lower:
                return DayDetector.DAY_LABELS[i]
        for i, day in enumerate(DayDetector.DAY_NAMES_FR):
            if day in header_lower:
                return DayDetector.DAY_LABELS[i]
        return None
