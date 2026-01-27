from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


# Detect a leading distance token, including ranges:
# - 6 km
# - 6.0km
# - 6.4-9.7 km
# - 5-10km
DIST_RE = re.compile(
    r"^\s*\d+(?:[\.,]\d+)?(?:\s*[-–]\s*\d+(?:[\.,]\d+)?)?\s*(?:km|mi|mile|miles)\b",
    re.IGNORECASE,
)

# Detect any distance mention anywhere (for a stricter 'bare label' check)
ANY_DIST_RE = re.compile(
    r"\b\d+(?:[\.,]\d+)?(?:\s*[-–]\s*\d+(?:[\.,]\d+)?)?\s*(?:km|mi|mile|miles)\b",
    re.IGNORECASE,
)


def iter_day_lines(output_text: str):
    for line in output_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        yield line


def extract_activity(day_line: str) -> str:
    # "Lundi: 6 km Run" -> "6 km Run"
    if ":" in day_line:
        return day_line.split(":", 1)[1].strip()
    return day_line.strip()


def main() -> None:
    dataset_path = Path(__file__).resolve().parents[1] / "running_week_training_dataset_from_final.json"
    data = json.loads(dataset_path.read_text(encoding="utf-8"))

    total_days = 0
    counts = Counter()
    no_dist = Counter()
    bare = Counter()

    for ex in data.get("training_data", []):
        output = ex.get("output", "")
        for day_line in iter_day_lines(output):
            total_days += 1
            activity = extract_activity(day_line)

            # Normalize only for counting
            activity_norm = activity.strip()

            # Focus on these categories
            for key in [
                "Intervals",
                "Tempo Run",
                "Hills",
                "Strides",
                "Marathon Pace",
            ]:
                if key in activity_norm:
                    counts[key] += 1
                    if not DIST_RE.search(activity_norm):
                        no_dist[key] += 1
                    # Bare: no distance anywhere in the activity string
                    if not ANY_DIST_RE.search(activity_norm):
                        bare[key] += 1
                    break

    print(f"Dataset: {dataset_path}")
    print(f"Total day lines: {total_days}")

    print("\nCounts:")
    for k in ["Intervals", "Tempo Run", "Hills", "Strides", "Marathon Pace"]:
        print(f"- {k}: {counts[k]} (no leading distance: {no_dist[k]}, bare(no distance anywhere): {bare[k]})")

    print("\nShare no-distance:")
    for k in ["Intervals", "Tempo Run", "Hills", "Strides", "Marathon Pace"]:
        if counts[k] == 0:
            continue
        pct = 100.0 * no_dist[k] / counts[k]
        pct_bare = 100.0 * bare[k] / counts[k]
        print(f"- {k}: no-leading-distance {pct:.1f}% | bare {pct_bare:.1f}%")


if __name__ == "__main__":
    main()
