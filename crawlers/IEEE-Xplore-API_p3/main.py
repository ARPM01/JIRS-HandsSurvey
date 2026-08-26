"""Collect IEEE Xplore metadata for the systematic-review search query."""

import csv
import json
from pathlib import Path

import xplore


SCRIPT_DIR = Path(__file__).resolve().parent
KEY_PATH = SCRIPT_DIR / "key.txt"
OUTPUT_DIR = SCRIPT_DIR / "data_foundation_agentic"
CSV_PATH = OUTPUT_DIR / "papers.csv"

CSV_FIELDS = [
    "article_number",
    "doi",
    "title",
    "authors",
    "publication_year",
    "publication_date",
    "publication_title",
    "content_type",
    "publisher",
    "abstract",
    "author_terms",
    "ieee_terms",
    "dynamic_index_terms",
    "conference_location",
    "conference_dates",
    "volume",
    "issue",
    "start_page",
    "end_page",
    "isbn",
    "issn",
    "access_type",
    "citing_paper_count",
    "citing_patent_count",
    "download_count",
    "html_url",
    "pdf_url",
    "abstract_url",
]

EMBODIMENT_QUERY = (
    '("robotic hand" OR "robot hand" OR "dexterous hand" OR '
    '"anthropomorphic hand" OR "artificial hand" OR '
    '"prosthetic hand" OR "bionic hand" OR '
    '"multifingered hand" OR "multi-fingered hand" OR '
    '"multifinger hand" OR "multi-finger hand" OR '
    '"five-finger hand" OR "five-fingered hand" OR '
    '"robotic palm" OR "robotic finger" OR '
    '"soft robotic hand" OR "tendon-driven hand" OR '
    '"multifingered gripper" OR "multi-fingered gripper" OR '
    '"dexterous gripper" OR "hand morphology" OR '
    '"finger synergy" OR "hand synergy" OR '
    '"dexterous grasp" OR "multifinger grasp" OR '
    '"multi-finger grasp")'
)

MANIPULATION_QUERY = (
    '(grasping OR "grasp generation" OR "functional grasping" OR '
    '"task-oriented grasping" OR "dexterous manipulation" OR '
    '"in-hand manipulation" OR "in hand manipulation" OR '
    '"object manipulation" OR "hand-object interaction" OR '
    '"finger control" OR "hand control")'
)

FOUNDATION_MODEL_QUERY = (
    '("foundation model" OR "foundation models" OR '
    '"robot foundation model" OR "robotics foundation model" OR '
    '"multimodal foundation model" OR '
    '"vision foundation model" OR "visual foundation model" OR '
    '"promptable foundation model" OR '
    '"large language model" OR LLM OR '
    '"vision-language model" OR "visual language model" OR VLM OR '
    '"vision-language-action model" OR "vision-language-action" OR '
    '"vision language action model" OR VLA OR '
    '"multimodal language model" OR '
    '"large multimodal model" OR '
    '"multimodal large language model" OR MLLM OR '
    '"vision-language policy" OR "multimodal policy" OR '
    '"generalist policy" OR "generalist robot policy" OR '
    '"general-purpose robot policy" OR '
    '"language-conditioned policy" OR '
    '"language-conditioned manipulation" OR '
    '"open-vocabulary manipulation" OR '
    '"tactile-language-action" OR '
    '"vision-language-tactile-action" OR '
    '"latent action representation")'
)

AGENTIC_QUERY = (
    '("agentic AI" OR '
    '"LLM-based planning" OR "LLM planner" OR '
    '"language-model-based planning" OR '
    '"VLM-based planning" OR "VLM planner" OR '
    '"vision-language planning" OR "multimodal planner" OR '
    '"language-guided planning" OR '
    '"language-guided task planning" OR '
    '"open-world planning" OR "task decomposition" OR '
    '"chain-of-thought" OR "robot chain-of-thought" OR '
    '"self-evaluation" OR "self-reflection" OR '
    '"reflection-based planning" OR '
    '"closed-loop reasoning" OR '
    '"autonomous reasoning" OR "reasoning-based manipulation" OR '
    '"failure recovery" OR "recovery mechanism")'
)

QUERY = (
    f"(({EMBODIMENT_QUERY}) OR ({MANIPULATION_QUERY})) AND "
    f"(({FOUNDATION_MODEL_QUERY}) OR ({AGENTIC_QUERY}))"
)
START_YEAR = "2019"
END_YEAR = "2026"
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


def flatten_authors(article: dict) -> str:
    """Return author names in publication order as a CSV-friendly string."""
    authors_container = article.get("authors") or {}
    if not isinstance(authors_container, dict):
        return ""

    authors = authors_container.get("authors") or []
    if not isinstance(authors, list):
        return ""

    names = []
    for author in authors:
        if not isinstance(author, dict):
            continue
        name = str(author.get("full_name") or "").strip()
        if name:
            names.append(name)
    return "; ".join(names)


def flatten_index_terms(article: dict, group_name: str) -> str:
    """Return one IEEE index-term group as a CSV-friendly string."""
    index_terms = article.get("index_terms") or {}
    if not isinstance(index_terms, dict):
        return ""

    group = index_terms.get(group_name) or {}
    if not isinstance(group, dict):
        return ""

    terms = group.get("terms") or []
    if isinstance(terms, str):
        terms = [terms]
    if not isinstance(terms, list):
        return ""

    return "; ".join(str(term).strip() for term in terms if str(term).strip())


def article_to_csv_row(article: dict) -> dict:
    """Flatten an IEEE article record into the columns used by papers.csv."""
    row = {field: article.get(field, "") for field in CSV_FIELDS}
    row["authors"] = flatten_authors(article)
    row["author_terms"] = flatten_index_terms(article, "author_terms")
    row["ieee_terms"] = flatten_index_terms(article, "ieee_terms")
    row["dynamic_index_terms"] = flatten_index_terms(
        article, "dynamic_index_terms"
    )
    return row


def initialize_csv() -> Path:
    """Create a fresh combined CSV for the current crawl."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
    return CSV_PATH


def append_articles_to_csv(articles: list[dict]) -> int:
    """Append one API page to the combined CSV and return its row count."""
    rows = [article_to_csv_row(article) for article in articles]
    with CSV_PATH.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    api_key = read_api_key()
    csv_path = initialize_csv()
    start_record = 1
    page_number = 0
    total_records = None
    csv_row_count = 0

    while True:
        payload = fetch_page(api_key, start_record)
        output_path = write_page(page_number, payload)
        articles = payload.get("articles", [])
        csv_row_count += append_articles_to_csv(articles)

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

    print(f"CSV: wrote {csv_row_count} records to {csv_path}")


if __name__ == "__main__":
    main()
