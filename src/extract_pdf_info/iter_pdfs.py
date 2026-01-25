from pathlib import Path
from typing import Iterable


def iter_pdfs(pdf_dir: Path) -> Iterable[Path]:
    if not pdf_dir.exists():
        return []
    return sorted(pdf_dir.glob("*.pdf"))
