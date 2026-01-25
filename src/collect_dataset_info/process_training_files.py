import csv
from pathlib import Path

from .extract_features import extract_features


def process_training_files(pdf_dir=None, xlsx_dir=None, output_file=None):
    """Traite tous les fichiers PDF et XLSX"""

    if pdf_dir is None:
        data_dir = Path("Data")
        pdf_dir = data_dir / "pdf"
    if xlsx_dir is None:
        data_dir = Path("Data")
        xlsx_dir = data_dir / "xlsx"
    if output_file is None:
        data_dir = Path("Data")
        output_file = data_dir / "training_analysis.csv"

    results = []

    if pdf_dir.exists():
        for pdf_file in sorted(pdf_dir.glob("*.pdf")):
            features = extract_features(pdf_file.name)
            results.append(
                {
                    "fichier": str(pdf_file),
                    "goal_distance": features["goal_distance"],
                    "goal_time": features["goal_time"],
                    "level": features["level"],
                    "weeks_training": features["weeks_training"],
                    "training_per_week": features["training_per_week"],
                    "age": features["age"],
                }
            )

    if xlsx_dir.exists():
        for xlsx_file in sorted(xlsx_dir.glob("*.xlsx")):
            features = extract_features(xlsx_file.name)
            results.append(
                {
                    "fichier": str(xlsx_file),
                    "goal_distance": features["goal_distance"],
                    "goal_time": features["goal_time"],
                    "level": features["level"],
                    "weeks_training": features["weeks_training"],
                    "training_per_week": features["training_per_week"],
                    "age": features["age"],
                }
            )

    if results:
        with output_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "fichier",
                    "goal_distance",
                    "goal_time",
                    "level",
                    "weeks_training",
                    "training_per_week",
                    "age",
                ],
            )
            writer.writeheader()
            writer.writerows(results)

        print(f"CSV genere: {output_file}")
        print(f"{len(results)} fichiers traites")
    else:
        print("Aucun fichier trouve dans Data/pdf ou Data/xlsx")
