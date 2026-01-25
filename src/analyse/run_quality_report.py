from pathlib import Path
from typing import Dict, Any, List

from .dataset_validator import DatasetValidator
from .quality_reporter import QualityReporter


def run_quality_report(csv_dir: Path = Path("Data/csv_optimized")) -> List[Dict[str, Any]]:
    if not csv_dir.exists():
        print(f"❌ Directory not found: {csv_dir}")
        return []

    csv_files = sorted(csv_dir.glob("*.csv"))
    print("=" * 80)
    print("🔍 VALIDATING OPTIMIZED DATASET")
    print("=" * 80)

    all_stats: List[Dict[str, Any]] = []

    for csv_file in csv_files:
        print(f"\n⏳ Validating: {csv_file.name}...", end=" ")
        stats = DatasetValidator.analyze_csv(csv_file)
        if stats:
            all_stats.append(stats)
            quality_pct = 100 * stats["valid_weeks"] / stats["total_weeks"]
            print(f"✅ {stats['total_weeks']} weeks ({quality_pct:.0f}% quality)")
        else:
            print("❌ FAILED")

    if not all_stats:
        print("\n❌ No valid CSV files found")
        return []

    QualityReporter.print_summary(all_stats)

    print("\n" + "=" * 80)
    print("📋 FILE-BY-FILE DETAILS")
    print("=" * 80)

    for stat in all_stats:
        QualityReporter.print_file_details(stat)

    print("\n" + "=" * 80)
    print("✅ VALIDATION COMPLETE")
    print("=" * 80)

    return all_stats
