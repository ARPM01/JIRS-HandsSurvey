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

Place your SerpApi key in a file named `key.txt` (one line, no trailing whitespace) in the `GS_crawler/` directory, then run:

```
python gs_crawler.py
```

Results are written as JSON files (`data_test/data_0.json`, `data_test/data_1.json`, ...).
Use `read_data.ipynb` to load and inspect the collected records.

---

## IEEE-Xplore-API_p3 - IEEE Xplore

Uses the official [IEEE Xplore Metadata API](https://developer.ieee.org/) (Python 3 port of the SDK) to retrieve metadata for matching articles.

**Search query:** `('hand' OR 'gripper') AND ('manipulation' OR 'grasping' OR 'grip' OR 'skill')`  
**Date range:** from 2019  
**Batch size:** 200 results per request (API maximum)

### Setup

```
pip install -r IEEE-Xplore-API_p3/requirements.txt
```

### Usage

Place your IEEE Xplore API key (obtained at <https://developer.ieee.org/member/register>) in a file named `key.txt` in the `IEEE-Xplore-API_p3/` directory, then run:

```
python main.py
```

Results are written as JSON files (`data_0.json`, `data_1.json`, ...).
Use `read_data.ipynb` to load and inspect the collected records.

**Note:** The bundled `xplore/xploreapi.py` is a modified version of the official Python 2.7 SDK, ported to Python 3 and patched to fix Error 400 responses from the `maximumResults` and `startingResult` parameters.
