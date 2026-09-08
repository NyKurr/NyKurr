import importlib.util
from datetime import date
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("render", Path(__file__).resolve().parents[1] / "scripts/render.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class SignalTests(unittest.TestCase):
    def test_private_or_unknown_visibility_rejected_before_commits(self):
        for meta in ({"private": True}, {}, {"private": False, "full_name": "other"}):
            calls = []
            def fetch(path):
                calls.append(path)
                return meta
            with self.assertRaises(ValueError):
                r.snapshot(date(2026, 9, 9), fetch)
            self.assertEqual(len(calls), 1)

    def test_week_boundaries_duplicates_and_future_commits(self):
        def fetch(path):
            if "commits?" not in path:
                return {"private": False, "full_name": r.REPO}
            return [{"sha": sha, "commit": {"committer": {"date": day + "T00:00:00Z"}}}
                    for sha, day in [("a", "2026-09-06"), ("b", "2026-09-07"),
                                     ("b", "2026-09-07"), ("c", "2026-09-10")]]
        data = r.snapshot(date(2026, 9, 9), fetch)
        self.assertEqual(data["counts"][-2:], [1, 1])
        self.assertEqual(sum(data["counts"]), 2)
        self.assertEqual(data["week_starts"][-1], "2026-09-07")
        r.validate(data)
        for svg in (r.identity(), r.signal(data)):
            ET.fromstring(svg)
            for forbidden in ("<script", "foreignObject", "https://", "http://api"):
                self.assertNotIn(forbidden, svg)

    def test_sensitive_extra_fields_rejected(self):
        data = {"repository": r.REPO, "as_of": "2026-09-09", "week_starts": [], "counts": [], "email": "private"}
        with self.assertRaises(ValueError):
            r.validate(data)


if __name__ == "__main__":
    unittest.main()
