from typing import Any, Dict, List, Optional

from .activity_cleaner import ActivityCleaner
from .day_detector import DayDetector
from .day_to_week_mapper import DayToWeekMapper
from .week_validator import WeekValidator


def process_table_numbered_format(table: List[List[Any]], headers: List[str]) -> Optional[List[Dict[str, str]]]:
    day_columns: Dict[int, int] = {}
    for col_idx, header in enumerate(headers):
        if not header:
            continue
        day_num = DayDetector.extract_day_number(header)
        if day_num is not None:
            day_columns[col_idx] = day_num
    if not day_columns:
        return None

    weeks_dict = DayToWeekMapper.group_day_columns_by_week(day_columns)
    training_data: List[Dict[str, str]] = []

    for row_idx in range(1, len(table)):
        row = table[row_idx]
        for week_num in sorted(weeks_dict.keys()):
            week_data: Dict[str, str] = {}
            dow_cols = weeks_dict[week_num]
            for dow in range(7):
                col_idx = dow_cols.get(dow)
                if col_idx is not None and col_idx < len(row):
                    cell_content = row[col_idx]
                    activity = ActivityCleaner.merge_multiline_activity(cell_content)
                else:
                    activity = "Rest"
                day_label = WeekValidator.DAY_LABELS[dow]
                week_data[day_label] = activity

            completed_week = WeekValidator.complete_week(week_data, week_num)
            if WeekValidator.validate_week(completed_week):
                training_data.append(completed_week)

    return training_data
