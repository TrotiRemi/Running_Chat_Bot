import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from collect_dataset_info.main import main as collect_dataset_info_main
from extract_pdf_info.main import main as extract_pdf_main
from clean_csv.main import main as clean_csv_main
from extract_xlsx_info.main import main as extract_xlsx_main
from csv_to_json.main import main as csv_to_json_main


def main() -> None:
    data_dir = PROJECT_ROOT / "Data"
    pdf_dir = data_dir / "pdf"
    xlsx_dir = data_dir / "xlsx"
    data_csv_dir = data_dir / "data_csv"
    data_csv_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Démarrage du pipeline intégré...\n")

    # 1) Collect dataset info
    print("📊 Étape 1: Extraction des informations des fichiers...")
    collect_dataset_info_main(pdf_dir, xlsx_dir, data_dir / "training_analysis.csv")

    # 2) Extract PDFs to CSV (temporary location for cleaning)
    print("\n📄 Étape 2: Extraction des PDFs...")
    temp_pdf_dir = data_dir / "temp_pdf_csv"
    extract_pdf_main(pdf_dir, temp_pdf_dir)

    # 3) Clean extracted PDF data
    print("\n🧹 Étape 3: Nettoyage des données PDF...")
    clean_csv_main(temp_pdf_dir, data_csv_dir)

    # 4) Extract XLSX to CSV (no cleaning needed)
    print("\n📊 Étape 4: Extraction des XLSX...")
    extract_xlsx_main(xlsx_dir, data_csv_dir)

    # 5) Create final JSON dataset
    print("\n📦 Étape 5: Création du dataset JSON final...")
    output_json = PROJECT_ROOT / "running_week_training_dataset_final.json"
    csv_to_json_main([data_csv_dir], str(output_json), augmentation_factor=2)

    # Clean up temporary directory
    import shutil
    if temp_pdf_dir.exists():
        try:
            shutil.rmtree(temp_pdf_dir)
        except Exception as e:
            print(f"⚠️  Impossible de supprimer le répertoire temporaire: {e}")

    print("\n✅ Pipeline complètement terminé!")


if __name__ == "__main__":
    main()
