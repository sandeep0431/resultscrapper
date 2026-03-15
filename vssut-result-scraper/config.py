from pathlib import Path

BASE_URL = "https://examinationresults.vssut.ac.in/result-data.php"

# Verified against the live portal for the supplied 2024 registration ranges.
RESULT_RID = "c20ad4d76fe97759aa27a0c99bff6710"
CCID = RESULT_RID

RANGE1_START = 2402070001
RANGE1_END = 2402070077

RANGE2_START = 2402070078
RANGE2_END = 2402070156

# Preferred format: add or remove tuples here as needed.
REGISTRATION_RANGES = [
    (RANGE1_START, RANGE1_END),
    (RANGE2_START, RANGE2_END),
]



REQUEST_DELAY = 1
REQUEST_TIMEOUT = 20
DEFAULT_WORKERS = 1

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_FILE = RESULTS_DIR / "ranking.xlsx"
SGPA_OUTPUT_FILE = RESULTS_DIR / "sgpa_ranking.xlsx"
CGPA_OUTPUT_FILE = RESULTS_DIR / "cgpa_ranking.xlsx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0.0.0 Safari/537.36"
    )
}
