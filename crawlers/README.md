# Crawlers

Scripts used to retrieve candidate papers for the systematic review from two sources.

## GS_crawler - Google Scholar

Uses the [SerpApi](https://serpapi.com/) Google Scholar engine to retrieve search results.

**Search query:** `("hand" OR "gripper") AND ("manipulation" OR "grasping" OR "grip" OR "skill")`

**Date range:** 2019-2025

**Pagination:** 50 pages x 20 results = up to 1000 records

### Setup

```
pip install google-search-results
```

### Usage

Place your SerpApi key in a file named `key.txt` (one line, no trailing whitespace) in the `GS_crawler/` directory. From the `crawlers/` directory, run:

```
cd GS_crawler
python gs_crawler.py
```

### Where to see the output

All paths below are relative to `crawlers/GS_crawler/`:

| Output | Location | Contents |
|---|---|---|
| Successful pages | `data/data_0.json`, `data/data_1.json`, ... | Complete SerpApi responses containing `organic_results` |
| Failed pages | `errors/data_0.json`, `errors/data_1.json`, ... | Empty or error responses that still failed after three attempts |
| Crawl summary | `crawl_summary.json` | Query settings plus successful and failed page offsets |
| Combined screening CSV | `articles_gs_ieee_new_filtered.csv` | Created only after running the export cell in `read_data.ipynb`; combines processed Scholar and IEEE records |

The crawler prints the result count for each successful page and reports the
number of successful and failed pages when it finishes. Open
`crawl_summary.json` for the quickest run-level status check, or inspect the
files under `data/` for the raw results.

To process and inspect the results, start Jupyter from the crawler directory so
the notebook's relative paths resolve correctly:

```
cd GS_crawler
jupyter notebook read_data.ipynb
```

The notebook loads `data/data_*.json`, filters and summarizes the Scholar
records, optionally loads IEEE files from `../IEEE-Xplore-API_p3/data/`, and can
write the combined semicolon-delimited CSV listed above.

---

## IEEE-Xplore-API_p3 - IEEE Xplore

Uses the official [IEEE Xplore Metadata API](https://developer.ieee.org/) (Python 3 port of the SDK) to retrieve metadata for matching articles.

**Search query:** `('hand' OR 'gripper') AND ('manipulation' OR 'grasping' OR 'grip' OR 'skill')`

**Date range:** 2019-2025

**Batch size:** 200 results per request (API maximum)

### Setup

```
pip install -r IEEE-Xplore-API_p3/requirements.txt
```

### Usage

Place your IEEE Xplore API key (obtained at <https://developer.ieee.org/member/register>) in a file named `key.txt` in the `IEEE-Xplore-API_p3/` directory. From the `crawlers/` directory, run:

```
cd IEEE-Xplore-API_p3
python main.py
```

### Where to see the output

Results are written under `crawlers/IEEE-Xplore-API_p3/data/`:

```
data/data_0.json
data/data_1.json
data/data_2.json
...
```

Each file contains one IEEE API response with up to 200 records in its
`articles` array. The first response also contains `total_records`. During the
crawl, the terminal prints the page number, number of records, starting record,
and complete output path for every file.

To load, deduplicate, filter, and plot the collected records:

```
cd IEEE-Xplore-API_p3
jupyter notebook read_data.ipynb
```

The notebook discovers every `data/data_*.json` file, prints raw and unique
article counts, and displays plots and filtered counts in the notebook itself.
It does not write a separate processed output file.

**Note:** The bundled `xplore/xploreapi.py` is a modified version of the official Python 2.7 SDK, ported to Python 3 and patched to fix Error 400 responses from the `maximumResults` and `startingResult` parameters.
