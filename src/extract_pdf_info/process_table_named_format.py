from typing import Any, Dict, List, Optional

from .activity_cleaner import ActivityCleaner
from .day_detector import DayDetector
from .week_validator import WeekValidator


def process_table_named_format(table: List[List[Any]], headers: List[str]) -> Optional[List[Dict[str, str]]]:
    day_columns: Dict[int, str] = {}
    for col_idx, header in enumerate(headers):
        if not header:
            continue
        day_name = DayDetector.extract_day_name(header)
        if day_name:
            day_columns[col_idx] = day_name
    if not day_columns:
        return None

    training_data: List[Dict[str, str]] = []
    week_num = 1

    for row_idx in range(1, len(table)):
        row = table[row_idx]
        week_data: Dict[str, str] = {}
        for col_idx in sorted(day_columns.keys()):
            day_name = day_columns[col_idx]
            cell_content = row[col_idx] if col_idx < len(row) else ""
            activity = ActivityCleaner.merge_multiline_activity(cell_content) if cell_content else "Rest"
            week_data[day_name] = activity

        completed_week = WeekValidator.complete_week(week_data, week_num)
        if WeekValidator.validate_week(completed_week):
            training_data.append(completed_week)
            week_num += 1

    return training_data
