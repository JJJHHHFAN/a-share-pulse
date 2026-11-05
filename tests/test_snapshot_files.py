"""Validate the committed snapshot bundle offline, using its actual archived data."""

import json
import math
from pathlib import Path
import unittest


DATA = Path(__file__).resolve().parents[1] / "docs/data"


class SnapshotFilesTest(unittest.TestCase):
    def test_script_payload_matches_json_files(self):
        latest = json.loads((DATA / "latest.json").read_text(encoding="utf-8"))
        history = json.loads((DATA / "history.json").read_text(encoding="utf-8"))
        script = (DATA / "market.js").read_text(encoding="utf-8")
        prefix = "window.__MARKET__ = "
        separator = ";\nwindow.__HISTORY__ = "
        self.assertTrue(script.startswith(prefix))
        snapshot_text, history_text = script[len(prefix):].split(separator, 1)
        self.assertEqual(json.loads(snapshot_text), latest)
        self.assertEqual(json.loads(history_text.rstrip().removesuffix(";")), history)

    def test_history_is_ordered_unique_and_matches_archives(self):
        history = json.loads((DATA / "history.json").read_text(encoding="utf-8"))
        dates = [item["date"] for item in history]
        self.assertEqual(dates, sorted(set(dates)))
        for item in history:
            if item.get("source") == "backfill":
                continue
            archive = json.loads((DATA / "history" / f"{item['date']}.json").read_text(encoding="utf-8"))
            self.assertEqual({k: v for k, v in item.items() if k != "source"}, archive)
        latest = json.loads((DATA / "latest.json").read_text(encoding="utf-8"))
        self.assertEqual(dates[-1], latest["date"])
        self.assertEqual(history[-1]["turnover"], latest["turnover"])

    def test_latest_numeric_values_are_finite(self):
        def check(value):
            if isinstance(value, dict):
                for child in value.values():
                    check(child)
            elif isinstance(value, list):
                for child in value:
                    check(child)
            elif isinstance(value, float):
                self.assertTrue(math.isfinite(value), value)

        check(json.loads((DATA / "latest.json").read_text(encoding="utf-8")))
