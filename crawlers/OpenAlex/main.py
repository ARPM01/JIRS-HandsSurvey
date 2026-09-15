"""Collect reproducible OpenAlex paper sets using PyAlex.

All searches cover 2019–2026. Set 1 supplies generative-haptics context;
Set 2 requires robot/robotic hand phrases. Each set has a separate CSV export.
The current queries search titles and abstracts.

Run these examples from crawlers/OpenAlex/ with dependencies installed:

    # Inspect compiled queries without making API requests.
    python main.py --set all --dry-run

    # Pilot one set at a time (ranked and seeded random samples).
    python main.py --set 1 --pilot
    python main.py --set 2 --pilot

    # Retrieve at most 500 records per query chunk into a fresh directory.
    python main.py --set all --max-records-per-query 500 --output-dir runs/final-capped

    # Resume failed/interrupted queries using the same settings.
    python main.py --set all --max-records-per-query 500 --output-dir runs/final-capped --resume

    # Rebuild CSV exports from saved pages without accessing the API.
    python main.py --rebuild runs/final-capped

Provide OPENALEX_API_KEY or a key.txt file alongside this module for retrieval.
Dry runs and offline rebuilding need no key. Full retrieval is uncapped unless
--max-records-per-query is specified; pilots default to 100 records per chunk.
Capped and pilot runs are marked partial. Use a new output directory when
changing settings; resume skips completed, capped, and finished pilot queries.
Run python main.py --help for all options.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

from queries import END_YEAR, START_YEAR, compile_queries

ROOT = Path(__file__).resolve().parent
FIELDS = ["openalex_id", "doi", "title", "authors", "publication_year",
          "publication_date", "venue", "work_type", "abstract", "cited_by_count",
          "landing_page_url", "pdf_url", "is_oa", "is_retracted",
          "set_id", "query_ids", "retrieval_role",
          "sample_modes", "doi_duplicate_candidate"]
FILES = {"1": "set_1_broad_context.csv", "2": "set_2_robot_haptics_bridge.csv",
         "3": "set_3_foundation_agentic.csv"}


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def write_csv(path, fields, rows):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(work):
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    best = work.get("best_oa_location") or {}
    index = work.get("abstract_inverted_index") or {}
    abstract = " ".join(word for pos, word in sorted(
        (pos, word) for word, positions in index.items() for pos in positions))
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "",
                 (work.get("doi") or "").strip(), flags=re.I).lower()
    return dict(
        openalex_id=work["id"], doi=doi, title=work.get("display_name") or "",
        authors="; ".join((a.get("author") or {}).get("display_name") or ""
                          for a in work.get("authorships") or []),
        publication_year=work.get("publication_year"),
        publication_date=work.get("publication_date"), venue=source.get("display_name"),
        work_type=work.get("type"), abstract=abstract,
        cited_by_count=work.get("cited_by_count"),
        landing_page_url=location.get("landing_page_url"),
        pdf_url=best.get("pdf_url") or location.get("pdf_url"),
        is_oa=(work.get("open_access") or {}).get("is_oa"),
        is_retracted=work.get("is_retracted"))


def rebuild(run):
    """Use only each query's current successful/capped attempt, never failed pages."""
    manifest = read_json(run / "manifest.json")
    sets = {set_id: {} for set_id in FILES}
    matches = []
    raw_hits = 0
    for query in manifest["queries"]:
        if query["status"] not in ("complete", "capped", "pilot"):
            continue
        for page in query["pages"]:
            payload = read_json(run / page)
            for work in payload["results"]:
                raw_hits += 1
                record = sets[query["set_id"]].setdefault(work["id"], {
                    "row": normalize(work), "queries": set(), "roles": set(), "modes": set()})
                record["queries"].add(query["id"])
                record["roles"].add(query["role"])
                record["modes"].add(payload["sample_mode"])
                matches.append((work["id"], query["set_id"], query["id"],
                                payload["sample_mode"]))
    doi_ids = {}
    for records in sets.values():
        for identifier, record in records.items():
            if record["row"]["doi"]:
                doi_ids.setdefault(record["row"]["doi"], set()).add(identifier)
    for set_id, records in sets.items():
        rows = []
        for identifier, record in sorted(records.items()):
            row = dict(record["row"], set_id=set_id,
                       query_ids=";".join(sorted(record["queries"])),
                       retrieval_role=";".join(sorted(record["roles"])),
                       sample_modes=";".join(sorted(record["modes"])),
                       doi_duplicate_candidate=len(doi_ids.get(record["row"]["doi"], [])) > 1)
            rows.append(row)
        write_csv(run / FILES[set_id], FIELDS, rows)
    write_csv(run / "query_matches.csv",
              ["openalex_id", "set_id", "query_id", "sample_mode"],
              [dict(zip(["openalex_id", "set_id", "query_id", "sample_mode"], m))
               for m in sorted(set(matches))])
    incomplete = [q["id"] for q in manifest["queries"] if q["status"] != "complete"]
    summary = dict(raw_hits=raw_hits, unique_counts={k: len(v) for k, v in sets.items()},
                   overlap_count=sum(
                       sum(identifier in records for records in sets.values()) > 1
                       for identifier in set().union(*sets.values())),
                   incomplete_queries=incomplete, partial=bool(incomplete),
                   zero_result_queries=[q["id"] for q in manifest["queries"]
                                        if q.get("reported_count") == 0],
                   work_types={k: {t: sum(r["row"]["work_type"] == t for r in v.values())
                                   for t in sorted({r["row"]["work_type"] or "" for r in v.values()})}
                               for k, v in sets.items()})
    write_json(run / "crawl_summary.json", summary)
    manifest["partial"] = bool(incomplete)
    write_json(run / "manifest.json", manifest)
    return summary


class ApiError(RuntimeError):
    """Sanitized API error, safe to persist."""
    pass


class StopRun(ApiError):
    pass


class Client:
    def __init__(self, key):
        import pyalex
        self.pyalex = pyalex
        pyalex.config.api_key = key
        # Handle retries here to distinguish budget/auth errors and keep timeouts bounded.
        pyalex.config.max_retries = 0

    def fetch(self, query, cursor="*", size=100, sample=None, seed=42, search_scope="fulltext"):
        import requests
        from pyalex.api import OpenAlexAuth
        request = self.pyalex.Works()
        if search_scope == "title_abstract":
            request = request.search_filter(title_and_abstract=query)
        else:
            request = request.search(query)
        request = request.filter(publication_year=f"{START_YEAR}-{END_YEAR}")
        if sample is not None:
            request = request.sample(sample, seed=seed)
        # Public get() has no timeout parameter in 0.21. Use the PyAlex-built
        # URL and auth with a timed session, retaining the complete JSON envelope.
        request.params.update({"per-page": size})
        if sample is None:
            request.params["cursor"] = cursor
        class TimedSession(requests.Session):
            def get(self, *args, **kwargs):
                kwargs.setdefault("timeout", (10, 60))
                return super().get(*args, **kwargs)
        for attempt in range(3):
            try:
                with TimedSession() as session:
                    response = session.get(request.url, auth=OpenAlexAuth(self.pyalex.config))
                    if response.status_code in (401, 403):
                        raise StopRun("OpenAlex authentication failed.")
                    if response.status_code == 429:
                        raise StopRun("OpenAlex rate/budget limit reached; resume later.")
                    if response.status_code in (500, 502, 503, 504) and attempt < 2:
                        time.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()
                    payload = response.json()
                if not isinstance(payload.get("results"), list) or not isinstance(payload.get("meta"), dict):
                    raise ValueError("Unexpected OpenAlex response shape.")
                return payload
            except (requests.Timeout, requests.ConnectionError):
                if attempt == 2:
                    raise ApiError("OpenAlex connection failed after three attempts.") from None
                time.sleep(2 ** attempt)
            except requests.HTTPError as exc:
                detail = exc.response.text[:1000]
                key = self.pyalex.config.api_key
                if key:
                    detail = detail.replace(key, "[REDACTED]")
                detail = re.sub(r"(api_key=)[^&\s\"]+", r"\1[REDACTED]", detail)
                raise ApiError(f"OpenAlex HTTP {exc.response.status_code}: {detail}") from None
        raise RuntimeError("OpenAlex retries exhausted.")


def crawl(run, settings, queries, client, resume=False):
    fingerprint = hashlib.sha256(json.dumps([settings, queries], sort_keys=True).encode()).hexdigest()
    manifest_path = run / "manifest.json"
    if resume:
        manifest = read_json(manifest_path)
        if manifest["fingerprint"] != fingerprint:
            raise ValueError("Resume settings/query mismatch; start a new run.")
    else:
        if run.exists() and any(run.iterdir()):
            raise ValueError("Output directory is not empty; choose a new directory or --resume.")
        run.mkdir(parents=True, exist_ok=True)
        manifest = dict(created_at=now(), settings=settings, fingerprint=fingerprint,
                        pyalex_version=version("pyalex"),
                        queries=[dict(q, status="pending", pages=[]) for q in queries])
        write_json(manifest_path, manifest)
    failed = False
    try:
        for query in manifest["queries"]:
            if query["status"] in ("complete", "pilot", "capped"):
                continue
            query.update(status="running", pages=[], retrieved_count=0,
                         attempt=uuid4().hex, started_at=now())
            write_json(manifest_path, manifest)
            print(f'{query["id"]}: starting (limit={settings["max_records"] or "unlimited"})', flush=True)
            try:
                cap = settings["max_records"]
                if settings["pilot"]:
                    ranked_size = (cap + 1) // 2
                    requests_to_make = [("ranked", ranked_size), ("random", cap - ranked_size)]
                    for mode, size in requests_to_make:
                        if not size:
                            continue
                        payload = client.fetch(query["expression"], size=size,
                                               sample=size if mode == "random" else None,
                                               seed=settings["seed"],
                                               search_scope=query.get("search_scope", "fulltext"))
                        save_page(run, query, payload, mode)
                        write_json(manifest_path, manifest)
                    query["status"] = "pilot"
                else:
                    cursor = "*"
                    seen = set()
                    while True:
                        size = min(100, cap - query["retrieved_count"]) if cap else 100
                        payload = client.fetch(query["expression"], cursor=cursor, size=size,
                                               search_scope=query.get("search_scope", "fulltext"))
                        save_page(run, query, payload, "cursor")
                        write_json(manifest_path, manifest)
                        next_cursor = payload["meta"].get("next_cursor")
                        if not payload["results"] or not next_cursor:
                            query["status"] = "complete"
                            break
                        if cap and query["retrieved_count"] >= cap:
                            query["status"] = "capped"
                            break
                        if next_cursor in seen:
                            raise ValueError("Repeated pagination cursor.")
                        seen.add(next_cursor)
                        cursor = next_cursor
                query["finished_at"] = now()
            except Exception as exc:
                # Do not persist arbitrary exception text: URLs may contain credentials.
                query["status"] = "failed"
                query["error"] = str(exc) if isinstance(exc, ApiError) else type(exc).__name__
                write_json(run / "errors" / (query["id"] + ".json"),
                           {"query_id": query["id"], "error": query["error"], "time": now()})
                failed = True
                if isinstance(exc, StopRun):
                    break
            finally:
                write_json(manifest_path, manifest)
            print(f'{query["id"]}: {query["status"]}, {query["retrieved_count"]} records')
    finally:
        write_json(manifest_path, manifest)
        rebuild(run)
        write_trials(run, manifest)
    return 1 if failed else 0


def save_page(run, query, payload, mode):
    count = payload["meta"].get("count")
    if not isinstance(count, int) or count < 0:
        raise ValueError("Missing/invalid result count.")
    for work in payload["results"]:
        if not work.get("id") or not START_YEAR <= (work.get("publication_year") or 0) <= END_YEAR:
            raise ValueError("Invalid work ID or out-of-range year.")
    page = Path("raw") / query["id"] / query["attempt"] / f'page_{len(query["pages"]) + 1:06}.json'
    write_json(run / page, dict(payload, sample_mode=mode))
    query["pages"].append(str(page))
    if mode != "random":
        query["reported_count"] = count
    query["retrieved_count"] += len(payload["results"])
    print(f'{query["id"]}: page {len(query["pages"])} ({mode}), '
          f'{query["retrieved_count"]} retrieved; '
          f'{query.get("reported_count", "?")} total matches', flush=True)


def write_trials(run, manifest):
    path = run / "query_trials.csv"
    previous = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            previous = {r["query_id"]: r for r in csv.DictReader(f)}
    fields = ["set_id", "query_id", "expression", "reported_count",
              "sample_size", "status", "seed", "relevant", "irrelevant", "uncertain",
              "seed_coverage", "decision"]
    rows = []
    for q in manifest["queries"]:
        old = previous.get(q["id"], {})
        row = {k: old.get(k, "") for k in fields}
        row.update(set_id=q["set_id"], query_id=q["id"],
                   expression=q["expression"], reported_count=q.get("reported_count", ""),
                   sample_size=q["retrieved_count"] if "retrieved_count" in q else 0,
                   status=q["status"], seed=manifest["settings"]["seed"])
        rows.append(row)
    write_csv(path, fields, rows)


def positive(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("Must be positive.")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", choices=["all", "1", "2", "3"], default="all")
    parser.add_argument("--pilot", action="store_true", help="Up to 50 ranked + 50 seeded random hits per chunk.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-records-per-query", type=positive,
                        help="Maximum records per request chunk (e.g. 500); default: uncapped.")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--rebuild", type=Path, help="Rebuild exports offline from a run directory.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.rebuild:
            print(json.dumps(rebuild(args.rebuild), indent=2))
            return 0
        if args.resume and not args.output_dir:
            raise ValueError("--resume requires --output-dir.")
        queries = compile_queries(args.set)
        settings = dict(start_year=START_YEAR,
                        end_year=END_YEAR, pilot=args.pilot, seed=args.seed,
                        max_records=min(args.max_records_per_query or 100, 100)
                        if args.pilot else args.max_records_per_query)
        if args.dry_run:
            print(json.dumps(dict(settings=settings, queries=queries), indent=2))
            return 0
        key = os.environ.get("OPENALEX_API_KEY", "").strip()
        if not key and (ROOT / "key.txt").exists():
            key = (ROOT / "key.txt").read_text().strip()
        if not key:
            raise ValueError("Set OPENALEX_API_KEY or create crawlers/OpenAlex/key.txt.")
        run = args.output_dir or ROOT / "runs" / (datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:6])
        print(f"Run directory: {run.resolve()}")
        return crawl(run, settings, queries, Client(key), args.resume)
    except KeyboardInterrupt:
        print("\nStopped. Raw pages are saved; restart with a new directory to change limits.")
        return 130
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
