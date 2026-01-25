from pathlib import Path
from typing import Dict, List, Optional

from .day_detector import DayDetector
from .header_cleaner import HeaderCleaner
from .process_table_named_format import process_table_named_format
from .process_table_numbered_format import process_table_numbered_format
from .table_deduplicator import TableDeduplicator
from .extract_training_tables import extract_training_tables


def process_pdf_file(pdf_path: Path) -> Optional[List[Dict[str, str]]]:
    print(f"\n📖 Processing: {pdf_path.name}")
    tables = extract_training_tables(pdf_path)
    if not tables:
        print("  ❌ No tables found")
        return None

    print(f"  📊 Found {len(tables)} tables")
    unique_tables = TableDeduplicator.deduplicate(tables)
    print(f"  ✅ After dedup: {len(unique_tables)} unique tables")

    all_training_data: List[Dict[str, str]] = []

    for table_idx, table in enumerate(unique_tables):
        if not table or len(table) < 2:
            continue
        headers = [HeaderCleaner.clean(h) for h in table[0]]
        print(f"  📋 Table {table_idx + 1}: Headers = {headers[:3]}...")
        format_type = DayDetector.detect_format(headers)
        print(f"     Format: {format_type}")
        if format_type == "named":
            training_data = process_table_named_format(table, headers)
        elif format_type == "numbered":
            training_data = process_table_numbered_format(table, headers)
        else:
            print("     ⚠️  Unknown format, skipping")
            continue
        if training_data:
            all_training_data.extend(training_data)
            print(f"     ✅ Extracted {len(training_data)} weeks")

    if all_training_data:
        print(f"  ✅ TOTAL: {len(all_training_data)} weeks")
        return all_training_data

    print("  ❌ No valid data extracted")
    return None
