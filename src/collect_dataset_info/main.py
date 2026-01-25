import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .process_training_files import process_training_files


def main(pdf_dir=None, xlsx_dir=None, output_file=None) -> None:
    process_training_files(pdf_dir, xlsx_dir, output_file)


if __name__ == "__main__":
    main()
