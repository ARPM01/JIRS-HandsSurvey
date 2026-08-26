"""Collect Google Scholar search results through SerpApi."""

import json
import time
from pathlib import Path

from serpapi import GoogleSearch


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "data"
ERROR_DIR = SCRIPT_DIR / "errors"
KEY_PATH = SCRIPT_DIR / "key.txt"

QUERY = (
    '("hand" OR "gripper") AND '
    '("manipulation" OR "grasping" OR "grip" OR "skill")'
)
START_YEAR = "2019"
END_YEAR = "2025"
PAGE_SIZE = 20
MAX_PAGES = 50
MAX_ATTEMPTS = 3


def read_api_key() -> str:
    try:
        api_key = KEY_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise RuntimeError(f"SerpApi key file not found: {KEY_PATH}") from exc

    if not api_key:
        raise RuntimeError(f"SerpApi key file is empty: {KEY_PATH}")
    return api_key


def fetch_page(api_key: str, start: int, sleep=time.sleep) -> dict:
    """Fetch one result page, retrying empty and failed responses."""
    last_response = {}

    for attempt in range(MAX_ATTEMPTS):
        params = {
            "engine": "google_scholar",
            "q": QUERY,
            "hl": "en",
            "as_ylo": START_YEAR,
            "as_yhi": END_YEAR,
            "start": start,
            "num": PAGE_SIZE,
            "api_key": api_key,
        }

        # An identical request can return a cached empty response. Bypass the
        # cache only after the first attempt to avoid unnecessary API usage.
        if attempt > 0:
            params["no_cache"] = True

        try:
            response = GoogleSearch(params).get_dict()
        except Exception as exc:
            response = {
                "error": f"{type(exc).__name__}: {exc}",
                "search_parameters": {
                    key: value for key, value in params.items() if key != "api_key"
                },
            }

        last_response = response
        if response.get("organic_results"):
            return response

        error = response.get("error", "No organic results returned")
        print(
            f"Start {start}: attempt {attempt + 1}/{MAX_ATTEMPTS} "
            f"failed: {error}"
        )

        if attempt + 1 < MAX_ATTEMPTS:
            sleep(2 ** attempt)

    return last_response


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def remove_stale_error_page(path: Path) -> None:
    """Remove an old error response from the successful-results directory."""
    if not path.exists():
        return

    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        existing = {}

    # Preserve a previously successful page when a later crawl attempt fails.
    if not existing.get("organic_results"):
        path.unlink()


def main() -> None:
    api_key = read_api_key()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ERROR_DIR.mkdir(parents=True, exist_ok=True)

    successful_pages = []
    failed_pages = []

    for page_number in range(MAX_PAGES):
        start = page_number * PAGE_SIZE
        response = fetch_page(api_key, start)
        results = response.get("organic_results", [])

        if not results:
            failed_pages.append({
                "page": page_number,
                "start": start,
                "error": response.get("error", "No organic results returned"),
            })
            write_json(ERROR_DIR / f"data_{page_number}.json", response)
            remove_stale_error_page(OUTPUT_DIR / f"data_{page_number}.json")
            continue

        successful_pages.append({
            "page": page_number,
            "start": start,
            "results": len(results),
        })
        write_json(OUTPUT_DIR / f"data_{page_number}.json", response)
        print(f"Page {page_number}: wrote {len(results)} results")

    summary = {
        "query": QUERY,
        "start_year": START_YEAR,
        "end_year": END_YEAR,
        "page_size": PAGE_SIZE,
        "max_pages": MAX_PAGES,
        "max_attempts": MAX_ATTEMPTS,
        "successful_pages": successful_pages,
        "failed_pages": failed_pages,
    }
    write_json(SCRIPT_DIR / "crawl_summary.json", summary)

    print(
        f"Completed with {len(successful_pages)} successful pages and "
        f"{len(failed_pages)} failed pages."
    )
    if failed_pages:
        print("Failed offsets:", [page["start"] for page in failed_pages])
        print(f"Failure details: {ERROR_DIR}")


if __name__ == "__main__":
    main()
