"""Collect IEEE Xplore metadata for the systematic-review search query."""

import json
from pathlib import Path

import xplore


SCRIPT_DIR = Path(__file__).resolve().parent
KEY_PATH = SCRIPT_DIR / "key.txt"
OUTPUT_DIR = SCRIPT_DIR / "data"

QUERY = "('hand' OR 'gripper') AND ('manipulation' OR 'grasping' OR 'grip' OR 'skill')"
START_YEAR = "2019"
END_YEAR = "2025"
MAX_RESULTS = 200


def read_api_key() -> str:
    try:
        api_key = KEY_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise RuntimeError(f"IEEE API key file not found: {KEY_PATH}") from exc

    if not api_key:
        raise RuntimeError(f"IEEE API key file is empty: {KEY_PATH}")
    return api_key


def parse_response(raw_response: str) -> dict:
    """Validate and decode a raw IEEE API response."""
    body = raw_response.strip()

    if "Developer Inactive" in body:
        raise RuntimeError(
            "IEEE Xplore rejected the request because the developer account or "
            "API key is inactive. Sign in at https://developer.ieee.org/, verify "
            "the account, and confirm that an approved Xplore Metadata API key "
            "is active under My Account."
        )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        preview = body[:200] if body else "<empty response>"
        raise RuntimeError(
            "IEEE Xplore returned a non-JSON response: " + preview
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError("IEEE Xplore returned JSON with an unexpected structure.")

    if payload.get("error"):
        raise RuntimeError(f"IEEE Xplore API error: {payload['error']}")

    return payload


def fetch_page(api_key: str, start_record: int) -> dict:
    query = xplore.XPLORE(api_key)
    query.booleanText(QUERY)
    query.resultsFilter("start_year", START_YEAR)
    query.resultsFilter("end_year", END_YEAR)
    query.resultsSorting("article_number", "asc")
    query.startingResult(start_record)
    query.maximumResults(MAX_RESULTS)
    return parse_response(query.callAPI())


def write_page(page_number: int, payload: dict) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"data_{page_number}.json"
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    api_key = read_api_key()
    start_record = 1
    page_number = 0
    total_records = None

    while True:
        payload = fetch_page(api_key, start_record)
        output_path = write_page(page_number, payload)
        articles = payload.get("articles", [])

        if total_records is None:
            try:
                total_records = int(payload["total_records"])
            except (KeyError, TypeError, ValueError) as exc:
                raise RuntimeError(
                    "IEEE response does not contain a valid total_records value."
                ) from exc
            print(f"Total number of results: {total_records}")

        print(
            f"Page {page_number}: wrote {len(articles)} records "
            f"starting at {start_record} to {output_path}"
        )

        if not articles or start_record + MAX_RESULTS > total_records:
            break

        # IEEE start_record is a one-based sequence offset. Advance by the
        # requested page size even when a response contains fewer records;
        # advancing by len(articles) can overlap the next page.
        start_record += MAX_RESULTS
        page_number += 1


if __name__ == "__main__":
    main()
