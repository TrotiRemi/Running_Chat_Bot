import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .config import OUTPUT_FILE
from .create_week_dataset import create_week_dataset
from .save_dataset import save_dataset


def main(input_dirs=None, output_file=None, augmentation_factor=2) -> None:
    if input_dirs is not None:
        # Temporarily override INPUT_DIRS
        import src.csv_to_json.config as config
        original_dirs = config.INPUT_DIRS
        config.INPUT_DIRS = input_dirs
    
    if output_file is None:
        output_file = OUTPUT_FILE
    
    dataset = create_week_dataset(augmentation_factor=augmentation_factor)
    save_dataset(dataset, output_file)
    
    if input_dirs is not None:
        config.INPUT_DIRS = original_dirs


if __name__ == "__main__":
    main()
