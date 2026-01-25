import csv
from pathlib import Path
from typing import List, Any

from .build_column_map import build_column_map
from .config import DAYS, OUTPUT_DIR, SHEET_NAME
from .find_header_row import find_header_row
from .is_week_value import is_week_value
from .normalize_text import normalize_text
from .read_sheet_rows import read_sheet_rows


def convert_workbook(xlsx_path: Path, output_csv: Path) -> None:
    rows = read_sheet_rows(xlsx_path, SHEET_NAME)
    if not rows:
        return

    header_idx = find_header_row(rows)
    header_row = rows[header_idx]
    col_map = build_column_map(header_row)

    output_rows: List[List[str]] = [["Week"] + DAYS]

    r = header_idx + 1
    while r < len(rows):
        week_cell = rows[r][col_map["week"]] if col_map["week"] < len(rows[r]) else None
        if not is_week_value(week_cell):
            r += 1
            continue

        week_value = str(int(float(normalize_text(week_cell, add_km=False))))

        next_r = r + 1
        while next_r < len(rows):
            next_week_cell = rows[next_r][col_map["week"]] if col_map["week"] < len(rows[next_r]) else None
            if is_week_value(next_week_cell):
                break
            next_r += 1

        combined_days: List[str] = []
        for day in DAYS:
            col_idx = col_map.get(day.lower())
            if col_idx is None:
                combined_days.append("")
                continue
            parts: List[str] = []
            for rr in range(r, next_r):
                if col_idx < len(rows[rr]):
                    text = normalize_text(rows[rr][col_idx])
                    if text:
                        parts.append(text)
            combined_days.append("; ".join(parts).strip())

        output_rows.append([week_value] + combined_days)
        r = next_r

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output_rows)
