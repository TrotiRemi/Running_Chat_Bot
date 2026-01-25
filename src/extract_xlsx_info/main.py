import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .config import INPUT_DIR
from .convert_workbook import convert_workbook


def main(xlsx_dir=None, output_dir=None) -> None:
    if xlsx_dir is None:
        xlsx_dir = INPUT_DIR
    if output_dir is None:
        output_dir = INPUT_DIR.parent / "csv_final_2"
    
    if not xlsx_dir.exists():
        raise SystemExit(f"Input directory not found: {xlsx_dir}")

    xlsx_files = sorted(xlsx_dir.glob("*.xlsx"))
    if not xlsx_files:
        raise SystemExit(f"No .xlsx files found in {xlsx_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    for xlsx_path in xlsx_files:
        output_csv = output_dir / (xlsx_path.stem + ".csv")
        convert_workbook(xlsx_path, output_csv)

    print(f"✅ Converted {len(xlsx_files)} Excel files into {output_dir}")


if __name__ == "__main__":
    main()
