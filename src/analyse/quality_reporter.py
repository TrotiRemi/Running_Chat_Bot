from collections import Counter
from typing import Dict, Any, List


class QualityReporter:
    """Generate quality reports."""

    @staticmethod
    def print_summary(all_stats: List[Dict[str, Any]]) -> None:
        print("\n" + "=" * 80)
        print("📊 DATASET QUALITY SUMMARY")
        print("=" * 80)

        total_weeks = sum(s["total_weeks"] for s in all_stats)
        total_valid = sum(s["valid_weeks"] for s in all_stats)
        total_corrupted = sum(s["corrupted_weeks"] for s in all_stats)

        print(f"\n✅ Total Weeks: {total_weeks}")
        print(f"✅ Valid Weeks: {total_valid} ({100 * total_valid / total_weeks:.1f}%)")
        print(f"❌ Corrupted Weeks: {total_corrupted} ({100 * total_corrupted / total_weeks:.1f}%)")

        all_activity_types = Counter()
        for stat in all_stats:
            all_activity_types.update(stat["activity_types"])

        print("\n🏋️  Training Variety:")
        for category, count in all_activity_types.most_common(10):
            pct = 100 * count / sum(all_activity_types.values())
            print(f"   {category:15} → {count:4} ({pct:5.1f}%)")

        avg_activity_len = sum(s["avg_activity_length"] for s in all_stats) / len(all_stats)
        avg_training_days = sum(s["avg_training_days"] for s in all_stats) / len(all_stats)

        print(f"\n📏 Average Activity Length: {avg_activity_len:.1f} characters")
        print(f"📅 Average Training Days/Week: {avg_training_days:.1f}")

        all_issues = Counter()
        for stat in all_stats:
            all_issues.update(stat["issues"])

        if all_issues:
            print("\n⚠️  Top Issues:")
            for issue, count in all_issues.most_common(5):
                print(f"   {count:3}x | {issue}")

    @staticmethod
    def print_file_details(stat: Dict[str, Any]) -> None:
        print(f"\n📄 {stat['file']}")
        print(
            f"   Weeks: {stat['total_weeks']} | Valid: {stat['valid_weeks']} "
            f"| Quality: {100 * stat['valid_weeks'] / stat['total_weeks']:.1f}%"
        )

        print("   Activity Types:")
        for category, count in stat["activity_types"].most_common(5):
            print(f"      {category:15} → {count}")

        print(f"   Avg Length: {stat['avg_activity_length']:.1f} chars")
        print(f"   Avg Training: {stat['avg_training_days']:.1f} days/week")

        if stat["weeks_with_issues"]:
            print(f"   ⚠️  Issues in {len(stat['weeks_with_issues'])} weeks:")
            for issue_info in stat["weeks_with_issues"][:3]:
                print(f"      Week {issue_info['week_num']}: {issue_info['issues'][0]}")
            if len(stat["weeks_with_issues"]) > 3:
                print(f"      ... and {len(stat['weeks_with_issues']) - 3} more")
