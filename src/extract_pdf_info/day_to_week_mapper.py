from typing import Dict


class DayToWeekMapper:
    """Convert day numbers to week + day_of_week."""

    @staticmethod
    def map_day_number(day_num: int, format_type: str = "0-indexed") -> tuple[int, int]:
        if format_type == "0-indexed":
            week = (day_num // 7) + 1
            day_of_week = day_num % 7
        elif format_type == "1-indexed":
            week = ((day_num - 1) // 7) + 1
            day_of_week = (day_num - 1) % 7
        else:
            raise ValueError(f"Unknown format: {format_type}")
        return week, day_of_week

    @staticmethod
    def group_day_columns_by_week(day_columns_dict: Dict[int, int], format_type: str = "0-indexed") -> Dict[int, Dict[int, int]]:
        weeks_dict: Dict[int, Dict[int, int]] = {}
        for col_idx, day_num in day_columns_dict.items():
            week, dow = DayToWeekMapper.map_day_number(day_num, format_type)
            weeks_dict.setdefault(week, {})[dow] = col_idx
        return dict(weeks_dict)
