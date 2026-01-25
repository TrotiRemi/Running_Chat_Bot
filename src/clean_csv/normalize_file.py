import csv
from pathlib import Path

from .is_row_invalid import is_row_invalid
from .normalize_cell import normalize_cell


def normalize_file(csv_path: Path, output_path: Path) -> None:
    with csv_path.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    if not rows:
        return

    header = rows[0]
    normalized_rows = [header]

    for row in rows[1:]:
        if is_row_invalid(row):
            continue
        normalized_row = [row[0]] + [normalize_cell(cell) for cell in row[1:8]]
        if any(not cell.strip() for cell in normalized_row[1:]):
            continue
        normalized_rows.append(normalized_row)

    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(normalized_rows)
