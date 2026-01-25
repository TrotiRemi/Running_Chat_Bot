from pathlib import Path

INPUT_DIRS = [Path("Data/csv_final"), Path("Data/csv_final_2")]
OUTPUT_FILE = "running_week_training_dataset_from_final.json"
DAYS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
EN_TO_FR = dict(zip(DAYS_EN, DAYS_FR))
