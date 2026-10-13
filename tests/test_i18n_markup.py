"""Regression tests for translated headings containing intentionally styled HTML."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = {}

    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            attributes = dict(attrs)
            heading_id = attributes.get("id")
            if heading_id:
                self.headings[heading_id] = attributes


class TranslationMarkupTests(unittest.TestCase):
    def test_styled_heading_translations_use_html_binding(self):
        source = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        labels = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        parser = HeadingParser()
        parser.feed(source)

        for heading_id, key in (
            ("featured-title", "featuredTitle"),
            ("catalog-title", "catalogTitle"),
        ):
            with self.subTest(heading=heading_id):
                attributes = parser.headings[heading_id]
                self.assertEqual(attributes.get("data-i18n-html"), key)
                self.assertNotIn("data-i18n", attributes)
                self.assertEqual(labels.count(f"{key}: "), 2)
                self.assertEqual(
                    sum(
                        f"{key}: " in line and '<span class="period">.</span>' in line
                        for line in labels.splitlines()
                    ),
                    2,
                )


if __name__ == "__main__":
    unittest.main()
