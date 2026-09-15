# OpenAlex crawler

Retrieves three separate paper sets, searching titles and abstracts for
**2019–2026**:

- **Set 1:** broad generative-haptics context.
- **Set 2:** computational touch methods in robotics or tactile-sensor contexts.
- **Set 3:** the IEEE crawler's foundation-model/agentic-AI search, with the
  same terms and Boolean structure: `(embodiment OR manipulation) AND
  (foundation models OR agentic AI)`.

Set 3 mirrors `crawlers/IEEE-Xplore-API_p3/main.py`. OpenAlex uses its existing
title/abstract search scope; different databases and search fields mean the
results need not match IEEE Xplore. Sets 1 and 2 retain their existing expressions.

## Setup and commands

From the repository root:

~~~sh
.venv/bin/python -m pip install -r crawlers/OpenAlex/requirements.txt
cd crawlers/OpenAlex
~~~

Use the project virtual environment for the following commands. Set
OPENALEX_API_KEY or store the key in key.txt beside main.py.

~~~sh
# Inspect queries without network access.
python main.py --set all --dry-run

# Pilot one set at a time.
python main.py --set 1 --pilot
python main.py --set 2 --pilot
python main.py --set 3 --pilot

# Retrieve the IEEE-equivalent query into a fresh directory.
python main.py --set 3 --output-dir runs/foundation-agentic

# Bounded retrieval into a fresh directory.
python main.py --set all --max-records-per-query 500 --output-dir runs/final-capped

# Resume with the same settings.
python main.py --set all --max-records-per-query 500 --output-dir runs/final-capped --resume

# Rebuild exports offline.
python main.py --rebuild runs/final-capped
~~~

## Limits and progress

Full retrieval has no default record cap. Use --max-records-per-query 500
to limit each compiled query chunk; the current core has one per set.
The crawler prints progress and checkpoints the manifest after each page.

Pilots request up to 50 ranked and 50 seeded random records per chunk.
Use --max-records-per-query 40 for a smaller pilot; its allowance is split
between both modes. Seed defaults to 42. Samples can overlap, so 100 retrieved
records may yield fewer unique papers. Pilots and capped queries are partial.

Stop with Ctrl+C. A fresh directory is required when changing settings or
query text. Resume skips complete, capped, and finished pilot queries, and
restarts failed/interrupted queries in new attempt directories. Old attempts
remain available but are excluded from exports.

Exit codes: 0 successful execution (including deliberate caps/pilots),
1 retrieval failure, 2 configuration error, 130 interruption.
Check the summary's partial flag before treating output as complete.

## Outputs and provenance

Each run contains:

- set_1_broad_context.csv, set_2_robot_haptics_bridge.csv, and
  set_3_foundation_agentic.csv: separate UTF-8, comma-delimited metadata exports.
  Unselected sets contain headers only.
- manifest.json: exact query text, settings, fingerprint, library version,
  timestamps, counts, and page/attempt paths.
- raw/: full response records and metadata.
- query_matches.csv: work/set/request/sample-mode attribution.
- query_trials.csv: counts and manual review fields.
- crawl_summary.json: counts, overlap, work types, and incomplete queries.
- errors/: sanitized failure details.

Deduplication uses OpenAlex IDs within each set. Shared records remain in
each matching set; distinct IDs with a shared DOI are flagged rather than merged.
There is no union CSV or query-version column.

Edit CORE_QUERIES in queries.py to change the current core searches.
Use --set 1, --set 2, or --set 3 to select a search; --set all includes all three.
The summary overlap_count counts distinct works appearing in at least two sets.
Exact query snapshots and a fingerprint provide reproducibility and prevent incompatible
resumes without maintaining a version registry.


Keep manual screening annotations separately, keyed by OpenAlex ID; rebuilding
replaces generated paper CSVs and the match table. Review pilot relevance
and duplicate study versions before treating results as the survey corpus.

## Validation

From the repository root:

~~~sh
.venv/bin/python -m unittest discover -s crawlers/OpenAlex -p 'test_*.py'
~~~

The adapter uses PyAlex query construction/authentication with timed Requests
sessions and explicit cursor pagination. Title/abstract search uses the
documented legacy field filter, verified by the live pilot trials.
