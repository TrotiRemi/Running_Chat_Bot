from pathlib import Path
from typing import Any, List, Optional

import pdfplumber


def extract_training_tables(pdf_path: Path) -> Optional[List[List[List[Any]]]]:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_tables: List[List[List[Any]]] = []
            for page_idx, page in enumerate(pdf.pages):
                try:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
                except Exception as exc:
                    print(f"  ⚠️  Error on page {page_idx + 1}: {type(exc).__name__}")
                    continue
            return all_tables
    except Exception as exc:
        print(f"❌ Error reading PDF {pdf_path}: {exc}")
        return None
