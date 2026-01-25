import csv
from pathlib import Path
from typing import Dict, List


def export_to_csv(training_data: List[Dict[str, str]], output_path: Path) -> None:
    if not training_data:
        return
    with output_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["Week", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(training_data)
