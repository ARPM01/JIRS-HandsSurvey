# OpenAlex crawler

Retrieves two separate paper sets using the current recommended queries:
broad generative-haptics context and the robot-hand/tactile-generation bridge.
Both search titles and abstracts for **2019–2026**. Set 2 requires robot-hand
wording, including robot-qualified dexterous, anthropomorphic, and
multi-fingered hand alternatives.

The current expressions preserve the previously recommended v3 search
(456 Set 1 and 32 Set 2 matches at the pilot checks). The noisier experimental
modeling expansion is excluded. Query-version selection has been removed.

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

# Bounded retrieval into a fresh directory.
python main.py --set all --max-records-per-query 500 --output-dir runs/final-capped

# Resume with the same settings.
python main.py --set all --max-records-per-query 500 --output-dir runs/final-capped --resume

# Rebuild exports offline.
python main.py --rebuild runs/final-capped

# Optional topic/background diagnostics.
python main.py --set 2 --topic S2-04 --pilot
python main.py --set 1 --context --pilot
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

- set_1_broad_context.csv and set_2_robot_haptics_bridge.csv: separate UTF-8,
  comma-delimited metadata exports. The unselected set contains headers only.
- manifest.json: exact query text, settings, fingerprint, library version,
  timestamps, counts, and page/attempt paths.
- raw/: full response records and metadata.
- query_matches.csv: work/set/request/sample-mode attribution.
- query_trials.csv: counts and manual review fields.
- crawl_summary.json: counts, overlap, work types, and incomplete queries.
- errors/: sanitized failure details.

Deduplication uses OpenAlex IDs within each set. Shared records remain in
both sets; distinct IDs with a shared DOI are flagged rather than merged.
There is no union CSV or query-version column.

Edit CORE_QUERIES in queries.py to change the current core searches.
Diagnostic blocks and HAND are maintained in the same module. Exact query
snapshots and a fingerprint provide reproducibility and prevent incompatible
resumes without maintaining a version registry.

Historical run data and [pilot reports](pilot_review/REPORT.md) remain intact
as research records. Their old versioned commands are historical. Existing
runs can be rebuilt offline; start a fresh directory for new retrieval after
this refactor, because the old settings fingerprints differ.

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
