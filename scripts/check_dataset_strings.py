from __future__ import annotations

import re
from pathlib import Path


def main() -> None:
    dataset_path = Path(__file__).resolve().parents[1] / "running_week_training_dataset_from_final.json"
    text = dataset_path.read_text(encoding="utf-8")

    def count_exact(needle: str) -> int:
        return text.count(needle)

    print(f"Dataset: {dataset_path}")
    print("Counts (case-sensitive):")
    print(f"- 'Intervals repeats': {count_exact('Intervals repeats')}")
    print(f"- 'intervals repeats': {count_exact('intervals repeats')}")
    print(f"- 'Tempo Run': {count_exact('Tempo Run')}")
    print(f"- 'tempo run': {count_exact('tempo run')}")
    print(f"- 'Easy Run': {count_exact('Easy Run')}")

    print("\nRegex counts (case-sensitive):")
    print(f"- \\brepeats\\b: {len(re.findall(r'\\brepeats\\b', text))}")


if __name__ == "__main__":
    main()
