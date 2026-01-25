import re
from pathlib import Path

INPUT_DIR = Path("Data/csv_optimized")
OUTPUT_DIR = Path("Data/csv_final")

DAY_PLACEHOLDER_RE = re.compile(r"\bDAY\S*\b")
DAYS_RE = re.compile(r"\bDAYS\b")
PUNCT_ONLY_RE = re.compile(r"^[\W_]+$")

MILES_RE = re.compile(
    r"(?i)(\d+(?:\.\d+)?)(?:\s*-\s*(\d+(?:\.\d+)?))?\s*(mile|miles)\b"
)

K_DISTANCE_RE = re.compile(r"(?i)\b(\d+(?:\.\d+)?)\s*k\b")
MIN_RE = re.compile(r"(?i)\bmins?\b")
SEC_RE = re.compile(r"(?i)\bsecs?\b")

DISALLOWED_CHARS_RE = re.compile(r"[^A-Za-z0-9\s\.,:;!\-+/()@%]", re.UNICODE)

TOKEN_REPLACEMENTS = {
    "HMP": "half marathon pace",
    "HM": "half marathon",
    "MP": "marathon pace",
    "LSD": "long slow distance",
    "LT": "lactate threshold",
    "ST": "speed threshold",
    "MT": "marathon threshold",
    "TEMPROU": "tempo run",
    "TEMPOR": "tempo run",
    "LONGRU": "long run",
    "LONGR": "long run",
    "LONRGU": "long run",
    "TRACKR": "track",
    "TRACRKE": "track",
    "EPEATS": "repeats",
    "PEATS": "repeats",
    "RACED": "race day",
    "EAS": "easy",
    "PTIONA": "optional",
    "UN": "run",
}

OCR_REPLACEMENTS = [
    (re.compile(r"(?i)full[-\s]?bodx"), "Full-Body"),
    (re.compile(r"(?i)\w*odr[-\s]?tteigh\w*"), "Body-Weight"),
    (re.compile(r"(?i)bodx"), "Body"),
    (re.compile(r"(?i)run/?walk"), "Run and Walk"),
    (re.compile(r"(?i)race day!?"), "Race Day"),
    (re.compile(r"(?i)w/"), "with"),
    (re.compile(r"(?i)\bbody[-\s]?weight\b"), "Body-Weight"),
    (re.compile(r"(?i)\bfull[-\s]?body\b"), "Full-Body"),
    (re.compile(r"(?i)\beigh\b"), "Weight"),
]
