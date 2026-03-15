from __future__ import annotations

import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

import requests
from requests import RequestException
from tqdm import tqdm

from config import (
    BASE_URL,
    CCID,
    CGPA_OUTPUT_FILE,
    DEFAULT_WORKERS,
    HEADERS,
    RANGE1_END,
    RANGE1_START,
    RANGE2_END,
    RANGE2_START,
    RANGE3_END,
    RANGE3_START,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
    RESULT_RID,
    SGPA_OUTPUT_FILE,
)
from parser import parse_result_page
from ranking import build_ranking_dataframe, format_top_students, save_dataframe_to_excel


def generate_registration_numbers() -> list[str]:
    ranges = (
        range(RANGE1_START, RANGE1_END + 1),
        range(RANGE2_START, RANGE2_END + 1),
        range(RANGE3_START, RANGE3_END + 1),
    )
    return [str(regd_no) for registration_range in ranges for regd_no in registration_range]


def build_request_params(registration_number: str) -> dict[str, str]:
    return {
        "rid": RESULT_RID,
        "ccid": CCID,
        "rollno": registration_number,
        "Name": "",
    }


def fetch_result_page(
    session: requests.Session,
    registration_number: str,
) -> str | None:
    response = session.get(
        BASE_URL,
        params=build_request_params(registration_number),
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def scrape_registration_number(
    session: requests.Session,
    registration_number: str,
    delay: float,
) -> tuple[dict | None, str | None]:
    try:
        html = fetch_result_page(session, registration_number)
        result = parse_result_page(html, requested_regd_no=registration_number)
        if result is None:
            return None, f"{registration_number}: no result found or SGPA/CGPA missing"
        return result, None
    except RequestException as exc:
        return None, f"{registration_number}: request failed ({exc})"
    except Exception as exc:  # pragma: no cover - defensive fallback for live scraping
        return None, f"{registration_number}: parse failed ({exc})"
    finally:
        if delay > 0:
            time.sleep(delay)


def scrape_sequential(registration_numbers: Iterable[str], delay: float) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []

    with requests.Session() as session:
        for registration_number in tqdm(list(registration_numbers), desc="Scraping", unit="student"):
            record, error = scrape_registration_number(session, registration_number, delay)
            if record:
                records.append(record)
            if error:
                errors.append(error)

    return records, errors


def scrape_parallel(
    registration_numbers: Iterable[str],
    delay: float,
    workers: int,
) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []

    def worker(registration_number: str) -> tuple[dict | None, str | None]:
        with requests.Session() as session:
            return scrape_registration_number(session, registration_number, delay)

    registration_numbers = list(registration_numbers)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(worker, registration_number): registration_number
            for registration_number in registration_numbers
        }
        for future in tqdm(as_completed(futures), total=len(futures), desc="Scraping", unit="student"):
            record, error = future.result()
            if record:
                records.append(record)
            if error:
                errors.append(error)

    return records, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape VSSUT result pages and build SGPA and CGPA leaderboards."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=REQUEST_DELAY,
        help="Delay in seconds after each request per worker.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Number of concurrent workers. Use 1 for fully sequential scraping.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top students to print in the terminal.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory where the SGPA and CGPA Excel files will be saved.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workers = max(1, args.workers)
    registration_numbers = generate_registration_numbers()

    if workers == 1:
        records, errors = scrape_sequential(registration_numbers, delay=args.delay)
    else:
        records, errors = scrape_parallel(registration_numbers, delay=args.delay, workers=workers)

    sgpa_ranking_df = build_ranking_dataframe(records, metric="SGPA")
    cgpa_ranking_df = build_ranking_dataframe(records, metric="CGPA")
    output_dir = Path(args.output_dir) if args.output_dir else SGPA_OUTPUT_FILE.parent
    sgpa_output_path = output_dir / SGPA_OUTPUT_FILE.name
    cgpa_output_path = output_dir / CGPA_OUTPUT_FILE.name
    saved_sgpa_output_path = save_dataframe_to_excel(sgpa_ranking_df, sgpa_output_path)
    saved_cgpa_output_path = save_dataframe_to_excel(cgpa_ranking_df, cgpa_output_path)

    print()
    print(format_top_students(sgpa_ranking_df, metric="SGPA", limit=args.top))
    print()
    print(format_top_students(cgpa_ranking_df, metric="CGPA", limit=args.top))
    print()
    print(f"Saved SGPA ranking to: {saved_sgpa_output_path}")
    print(f"Saved CGPA ranking to: {saved_cgpa_output_path}")
    print(f"Scanned registration numbers: {len(registration_numbers)}")
    print(f"Valid results collected: {len(records)}")
    print(f"Skipped or failed: {len(errors)}")


if __name__ == "__main__":
    main()
