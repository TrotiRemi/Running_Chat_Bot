import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .extract_pdfs_to_csv import extract_pdfs_to_csv


def main(pdf_dir=None, output_dir=None) -> None:
    if pdf_dir is None:
        data_dir = Path("Data")
        pdf_dir = data_dir / "pdf"
    if output_dir is None:
        data_dir = Path("Data")
        output_dir = data_dir / "csv_optimized"
    extract_pdfs_to_csv(pdf_dir, output_dir)


if __name__ == "__main__":
    main()
