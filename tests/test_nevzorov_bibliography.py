"""Integrity checks for the public bibliography and its interactive viewer."""
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parents[1] / "web" / "nevzorov-science"

class BibliographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bib = json.loads((BASE / "bibliography.json").read_text(encoding="utf-8"))
        cls.rows = cls.bib["records"]

    def test_all_records(self):
        self.assertEqual(len(self.rows), 456)
        self.assertEqual(len({r["id"] for r in self.rows}), 456)

    def test_documented_statuses(self):
        self.assertEqual(sum(r["identification"] == "confirmed" for r in self.rows), 409)
        self.assertEqual(sum(r["relation"] == "identity_recorded" for r in self.rows), 101)

    def test_external_catalogs(self):
        self.assertEqual(sum(bool(r["catalog_url"]) for r in self.rows), 389)
        self.assertEqual(sum(bool(r["viewer_url"]) for r in self.rows), 7)
        for row in self.rows:
            for key in ("catalog_url", "viewer_url"):
                if row[key]:
                    u = urlsplit(row[key])
                    self.assertIn(u.scheme, ("http", "https"))
                    self.assertTrue(u.hostname)

    def test_archive_references(self):
        ids = {r["id"] for r in self.rows}
        total = 0
        for part in ("archives-a.json", "archives-b.json"):
            doc = json.loads((BASE / part).read_text(encoding="utf-8"))
            for bib_id, links in doc["by_bib"].items():
                self.assertIn(bib_id, ids)
                for link in links:
                    self.assertEqual(urlsplit(link["url"]).scheme, "https")
                    total += 1
        self.assertGreater(total, 45)

    def test_navigation(self):
        self.assertIn('href="bibliography.html"', (BASE / "index.html").read_text(encoding="utf-8"))
        self.assertIn('id="focus-graph"', (BASE / "bibliography.html").read_text(encoding="utf-8"))
        self.assertIn("archives-a.json", (BASE / "bibliography.js").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
