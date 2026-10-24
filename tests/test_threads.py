import datetime as dt
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from threadnotes import core  # noqa: E402
from threadnotes.__main__ import main  # noqa: E402

TODAY = dt.date(2026, 10, 24)


def notes():
    return {n["file"]: n for n in core.load(os.path.join(ROOT, "threads"))}


class Tests(unittest.TestCase):
    def test_healthy_note(self):
        self.assertEqual(core.problems(notes()["billing-migration.md"], TODAY), [])

    def test_overdue_and_stale(self):
        p = " ".join(core.problems(notes()["vendor-contract.md"], TODAY))
        self.assertIn("overdue", p)
        self.assertIn("stale", p)

    def test_missing_fields_and_body(self):
        p = core.problems(notes()["onboarding-doc.md"], TODAY)
        self.assertIn("missing field: owner", p)
        self.assertIn("missing field: source", p)
        self.assertIn("no 'where things stand' text", p)

    def test_done_notes_are_not_overdue(self):
        self.assertEqual(core.problems(notes()["old-audit.md"], TODAY), [])

    def test_index_orders_by_status_then_due(self):
        rows = [l for l in core.index_md(list(notes().values())).splitlines() if l.startswith("| ") and "Status" not in l and ":---" not in l]
        self.assertTrue(rows[0].startswith("| open"))
        self.assertTrue(rows[-1].startswith("| done"))

    def test_viewer_escapes_html(self):
        n = {"file": "x.md", "title": "<script>alert(1)</script>", "status": "open", "body": "<b>x</b>"}
        out = core.viewer_html([n], TODAY)
        self.assertNotIn("<script>alert", out)

    def test_cli_index_and_view(self):
        d = tempfile.mkdtemp()
        shutil.copytree(os.path.join(ROOT, "threads"), os.path.join(d, "t"))
        self.assertEqual(main(["index", os.path.join(d, "t")]), 0)
        self.assertEqual(main(["view", os.path.join(d, "t")]), 0)
        self.assertTrue(os.path.exists(os.path.join(d, "t", "INDEX.md")))
        self.assertTrue(os.path.exists(os.path.join(d, "t", "viewer.html")))


if __name__ == "__main__":
    unittest.main()
