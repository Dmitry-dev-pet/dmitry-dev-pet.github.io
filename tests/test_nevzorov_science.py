"""Public GitHub Pages graph must not leak the private Nevzorov Lab corpus."""
import json
import re
import unittest
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "web" / "nevzorov-science" / "index.html"
RESTRICTED = [
    r"drive\.google\.com",
    r"github\.com/Dmitry-dev-pet/nevzorov-lab",
    r"NVBOOK-GLEBYCH",
    r"/corpus/",
    r"/raw/manifests/",
    r"\.fb2(?:\.zip)?",
    r"ghp_[a-zA-Z0-9]+",
    r"ghs_[a-zA-Z0-9]+",
]
GRAPH_RE = re.compile(
    r'<script id="graph-json" type="application/json">([\s\S]*?)</script>'
)
DOI_RE = re.compile(r"^https://doi\.org/10\.\d{4,9}/\S+$")
NODE_TYPES = {"idea", "claim", "study", "finding"}
EDGE_TYPES = {
    "frames", "argument_sequence", "studies", "supports_narrowly",
    "provides_framework", "defines_criteria", "qualifies", "refines",
    "limits_generalization", "raises_question",
}

class NevzorovPublicGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        payload = GRAPH_RE.search(cls.html)
        if not payload:
            raise AssertionError("Missing self-contained JSON payload")
        cls.graph = json.loads(payload.group(1))

    def test_sanitized_content_only(self):
        for regex in RESTRICTED:
            self.assertNotRegex(self.html, re.compile(regex, re.I))
        self.assertFalse(re.search(r"<script[^>]+src=", self.html, re.I))
        self.assertFalse(re.search(r"<link[^>]+stylesheet", self.html, re.I))
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

    def test_expected_graph_structure(self):
        g = self.graph
        self.assertEqual(g["schema_version"], 1)
        self.assertEqual(set(g), {"schema_version", "map_id", "nodes", "edges"})
        self.assertEqual(len(g["nodes"]), 24)
        self.assertEqual(len(g["edges"]), 31)
        ids = {x["id"] for x in g["nodes"]}
        self.assertEqual(len(ids), 24)
        self.assertEqual(len({e["id"] for e in g["edges"]}), 31)
        for n in g["nodes"]:
            self.assertIn(n["type"], NODE_TYPES)
            self.assertEqual(set(n), {"id", "type", "label", "description", "status", "url", "year", "locator"})
        for e in g["edges"]:
            self.assertIn(e["kind"], EDGE_TYPES)
            self.assertIn(e["source"], ids)
            self.assertIn(e["target"], ids)
            self.assertTrue(e["note"])
            self.assertEqual(set(e), {"id", "source", "target", "kind", "evidence", "note"})

    def test_only_public_doi_outbound_links(self):
        urls = [n["url"] for n in self.graph["nodes"] if n["url"]]
        urls.extend(e["evidence"] for e in self.graph["edges"] if e["evidence"])
        self.assertEqual(len(urls), 24)
        self.assertTrue(all(DOI_RE.fullmatch(x) for x in urls))

    def test_post_2013_studies_not_claimed_as_historical_sources(self):
        studies = [n for n in self.graph["nodes"] if n["type"] == "study"]
        self.assertEqual(len(studies), 8)
        for study in studies:
            if study["year"] > 2013:
                self.assertIn("impossible_post_2013", study["description"])

if __name__ == "__main__":
    unittest.main()
