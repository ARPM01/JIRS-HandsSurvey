import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import requests

import main
from queries import compile_queries, CORE_QUERIES


def work(identifier="W1", **kw):
    return dict(id=identifier, publication_year=2022, display_name='Touch, "robot"\nhand',
                abstract_inverted_index={"touch": [1], "Robot": [0]}, **kw)


def page(records, cursor=None, count=1):
    return {"results": records, "meta": {"count": count, "next_cursor": cursor}}


class Fake:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.calls = []

    def fetch(self, expression, **kwargs):
        self.calls.append(kwargs)
        result = next(self.pages)
        if isinstance(result, BaseException):
            raise result
        return result


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.run = Path(self.temp.name) / "run"
        self.settings = dict(start_year=2019, end_year=2026,
                             pilot=False, seed=42, max_records=None)
        self.q = [dict(id="q1", set_id="1", role="core", expression="haptics"),
                  dict(id="q2", set_id="2", role="core", expression=CORE_QUERIES["2"])]

    def tearDown(self):
        self.temp.cleanup()

    def test_queries(self):
        self.assertEqual([q["set_id"] for q in compile_queries()], ["1", "2"])
        for selected in ("1", "2"):
            self.assertEqual([q["set_id"] for q in compile_queries(selected)], [selected])
        with self.assertRaises(ValueError):
            compile_queries("3")

    def test_current_query_scope_and_limits(self):
        for q in compile_queries():
            self.assertEqual(q["expression"], CORE_QUERIES[q["set_id"]])
            self.assertLessEqual(len(q["expression"]), 1400)
            self.assertEqual(q["search_scope"], "title_abstract")
        self.assertTrue(CORE_QUERIES["2"].startswith(
            '( (robot OR robotic OR robotics OR "tactile sensor"'))
        self.assertIn('"tactile prediction"', CORE_QUERIES["2"])
        self.assertNotIn('"tactile modeling"', CORE_QUERIES["2"])

    def test_scoped_api_and_sampling_keep_years(self):
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"meta":{"count":0},"results":[]}'
        with patch("requests.Session.get", return_value=response) as get:
            main.Client("test-key").fetch("tactile synthesis", sample=10,
                                         search_scope="title_abstract")
        url = get.call_args.args[0]
        self.assertIn("title_and_abstract.search", url)
        self.assertIn("2019-2026", url)
        self.assertIn("sample=10", url)

    def test_exact_cap_and_live_checkpoint(self):
        class CheckpointClient(Fake):
            def fetch(inner, expression, **kwargs):
                if inner.calls:
                    m = main.read_json(self.run / "manifest.json")
                    self.assertEqual(m["queries"][0]["retrieved_count"], 100)
                return super(CheckpointClient, inner).fetch(expression, **kwargs)
        records = [work(f"W{i}") for i in range(100)]
        fake = CheckpointClient([page(records, "next", 500), page([work("W100")], "next2", 500)])
        main.crawl(self.run, dict(self.settings, max_records=101), self.q[:1], fake)
        self.assertEqual([c["size"] for c in fake.calls], [100, 1])
        self.assertEqual(main.rebuild(self.run)["unique_counts"]["1"], 101)

    def test_pages_overlap_and_rebuild(self):
        fake = Fake([page([work()], "next"), page([work(), work("W2")]), page([work()])])
        self.assertEqual(main.crawl(self.run, self.settings, self.q, fake), 0)
        summary = main.rebuild(self.run)
        self.assertEqual(summary["unique_counts"], {"1": 2, "2": 1})
        self.assertEqual(summary["overlap_count"], 1)
        self.assertFalse(summary["partial"])
        self.assertFalse((self.run / "papers_union.csv").exists())
        with (self.run / main.FILES["1"]).open(newline="") as f:
            row = next(csv.DictReader(f))
        self.assertEqual(row["abstract"], "Robot touch")
        self.assertEqual(row["title"], work()["display_name"])

    def test_failed_attempt_resume_and_mismatch(self):
        fake = Fake([page([work("OLD")], "next"), RuntimeError("secret"), page([] , count=0)])
        self.assertEqual(main.crawl(self.run, self.settings, self.q, fake), 1)
        self.assertEqual(main.rebuild(self.run)["unique_counts"]["1"], 0)
        replacement = Fake([page([work("NEW")])])
        self.assertEqual(main.crawl(self.run, self.settings, self.q, replacement, True), 0)
        self.assertEqual(len(replacement.calls), 1)
        self.assertNotIn("secret", (self.run / "errors/q1.json").read_text())
        with self.assertRaises(ValueError):
            main.crawl(self.run, dict(self.settings, seed=1), self.q, replacement, True)

    def test_pilot_and_cap(self):
        settings = dict(self.settings, pilot=True, max_records=100)
        fake = Fake([page([work()], count=300), page([work("RANDOM")])])
        main.crawl(self.run, settings, self.q[:1], fake)
        self.assertEqual(fake.calls[1]["sample"], 50)
        self.assertTrue(main.rebuild(self.run)["partial"])
        self.assertEqual(main.read_json(self.run / "manifest.json")["queries"][0]["reported_count"], 300)

    def test_budget_stops_remaining_queries(self):
        fake = Fake([main.StopRun("Rate limit")])
        self.assertEqual(main.crawl(self.run, self.settings, self.q, fake), 1)
        self.assertEqual(len(fake.calls), 1)

    def test_client_filters_retries_and_timeout(self):
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"meta":{"count":0},"results":[]}'
        with patch("requests.Session.get", side_effect=[requests.Timeout(), response]) as get, patch("time.sleep"):
            main.Client("test-key").fetch("robot", sample=20)
        url = get.call_args.args[0]
        self.assertIn("2019-2026", url)
        self.assertEqual(get.call_args.kwargs["timeout"], (10, 60))
        self.assertEqual(get.call_count, 2)
        self.assertNotIn("test-key", url)

    def test_capped_null_metadata_duplicate_doi(self):
        settings = dict(self.settings, max_records=2)
        fake = Fake([page([work("W1", doi="https://doi.org/10/X"),
                                work("W2", doi="10/x")], "next", 100)])
        main.crawl(self.run, settings, self.q[:1], fake)
        summary = main.rebuild(self.run)
        self.assertTrue(summary["partial"])
        with (self.run / main.FILES["1"]).open() as f:
            self.assertTrue(all(r["doi_duplicate_candidate"] == "True" for r in csv.DictReader(f)))

    def test_interrupt_restarts_and_preserves_manual_trials(self):
        with self.assertRaises(KeyboardInterrupt):
            main.crawl(self.run, self.settings, self.q[:1],
                       Fake([page([work("OLD")], "next"), KeyboardInterrupt()]))
        self.assertTrue(main.rebuild(self.run)["partial"])
        trial = self.run / "query_trials.csv"
        with trial.open(newline="") as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        rows[0]["decision"] = "Review seed misses"
        main.write_csv(trial, fields, rows)
        main.crawl(self.run, self.settings, self.q[:1], Fake([page([work("NEW")])]), True)
        self.assertIn("Review seed misses", trial.read_text())
        self.assertNotIn("OLD", (self.run / main.FILES["1"]).read_text())

    def test_bad_year_and_interrupt(self):
        bad = work()
        bad["publication_year"] = 2018
        self.assertEqual(main.crawl(self.run, self.settings, self.q[:1], Fake([page([bad])])), 1)
        self.assertEqual(main.rebuild(self.run)["unique_counts"]["1"], 0)


if __name__ == "__main__":
    unittest.main()
