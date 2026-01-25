import hashlib
from typing import Any, List, Optional

from .header_cleaner import HeaderCleaner


class TableDeduplicator:
    """Remove duplicate tables from PDF extraction."""

    @staticmethod
    def hash_table(table: List[List[Any]], rows_to_use: int = 3) -> Optional[str]:
        if not table:
            return None
        sample = []
        for row_idx in range(min(rows_to_use, len(table))):
            normalized_row = []
            for cell in table[row_idx]:
                cell_str = HeaderCleaner.clean(str(cell)).lower()
                normalized_row.append(cell_str)
            sample.append(tuple(normalized_row))
        content = str(sample).encode()
        return hashlib.md5(content).hexdigest()

    @staticmethod
    def deduplicate(tables: List[List[List[Any]]]) -> List[List[List[Any]]]:
        unique_tables: List[List[List[Any]]] = []
        seen_hashes = set()
        for table in tables:
            table_hash = TableDeduplicator.hash_table(table)
            if table_hash and table_hash not in seen_hashes:
                unique_tables.append(table)
                seen_hashes.add(table_hash)
        return unique_tables
