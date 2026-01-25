import re
from typing import Any


class HeaderCleaner:
    """Clean OCR artifacts from table headers."""

    OCR_PATTERNS = [
        (r"=+\s*-+\s*=+", ""),
        (r"[=-]{2,}", ""),
        (r"o\s*ll(?::|::)", ""),
        (r"\.{2,}", ""),
        (r"II\.|ll::|::i", ""),
        (r"\s+[A-Z]{1,2}\s+[=-]", ""),
        (r"([^a-zA-Z0-9\s])\1+", r"\1"),
    ]

    @staticmethod
    def clean(text: Any) -> str:
        if not text:
            return ""
        text = str(text).strip()
        for pattern, replacement in HeaderCleaner.OCR_PATTERNS:
            text = re.sub(pattern, replacement, text)
        return re.sub(r"\s+", " ", text).strip()
