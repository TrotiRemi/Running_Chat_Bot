import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .config import INPUT_DIR, OUTPUT_DIR
from .normalize_file import normalize_file


def main(input_dir=None, output_dir=None) -> None:
    if input_dir is None:
        input_dir = INPUT_DIR
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    if not input_dir.exists():
        raise SystemExit(f"Input directory not found: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise SystemExit(f"No CSV files found in: {input_dir}")

    for csv_file in csv_files:
        output_file = output_dir / csv_file.name
        normalize_file(csv_file, output_file)

    print(f"✅ Normalized {len(csv_files)} files into {output_dir}")


if __name__ == "__main__":
    main()
