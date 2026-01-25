import csv
from pathlib import Path

from .clean_training_text import clean_training_text
from .config import DAYS_FR, DAYS_EN
from .get_day_value import get_day_value


def parse_csv_file(csv_path: Path):
    weeks = []
    try:
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                week_num = row.get("Week") or row.get("week") or row.get("WEEK")
                if not week_num:
                    continue
                try:
                    week_value = int(float(str(week_num).strip()))
                except ValueError:
                    continue

                week_data = {"week": week_value, "days": {}}

                for day_fr, day_en in zip(DAYS_FR, DAYS_EN):
                    training = get_day_value(row, day_fr, day_en)
                    cleaned = clean_training_text(training)
                    week_data["days"][day_fr.lower()] = cleaned

                weeks.append(week_data)

        return weeks
    except Exception as e:
        print(f"  ⚠️  Erreur parsing {csv_path.name}: {e}")
        return None
