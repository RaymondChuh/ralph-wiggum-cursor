"""Offline tests for lit_search parsers (no network). Run: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lit_search  # noqa: E402

ARXIV_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <published>2024-01-02T00:00:00Z</published>
    <title>An Instrumented Insole for
      Running Gait Event Detection</title>
    <summary>We present an insole...</summary>
    <author><name>Ada Lovelace</name></author>
    <author><name>Alan Turing</name></author>
  </entry>
</feed>"""

GITHUB_JSON = {
    "items": [
        {
            "full_name": "someone/open-insole",
            "html_url": "https://github.com/someone/open-insole",
            "pushed_at": "2025-03-04T00:00:00Z",
            "license": {"spdx_id": "MIT"},
            "stargazers_count": 42,
            "description": "Open smart insole with 8 FSRs and an IMU",
        },
        {
            "full_name": "x/y",
            "html_url": "https://github.com/x/y",
            "pushed_at": None,
            "license": {"spdx_id": "NOASSERTION"},
            "stargazers_count": 0,
            "description": None,
        },
    ]
}

OPENALEX_JSON = {
    "results": [
        {
            "display_name": "Validity of insole-derived contact time in running",
            "publication_year": 2022,
            "doi": "https://doi.org/10.1234/abcd",
            "cited_by_count": 7,
            "open_access": {"oa_status": "gold"},
            "primary_location": {"license": "cc-by"},
            "authorships": [{"author": {"display_name": "Grace Hopper"}}],
        }
    ]
}

PUBMED_JSON = {
    "result": {
        "uids": ["123"],
        "123": {
            "title": "Plantar pressure insoles in runners.",
            "pubdate": "2021 Mar",
            "source": "Sensors (Basel)",
            "authors": [{"name": "Curie M"}, {"name": "Noether E"}],
        },
    }
}


class ParserTests(unittest.TestCase):
    def test_arxiv(self):
        rows = lit_search.parse_arxiv(ARXIV_XML)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r["title"], "An Instrumented Insole for Running Gait Event Detection")
        self.assertEqual(r["year"], "2024")
        self.assertEqual(r["id"], "lovelace2024-an-instrumented-insole-for")
        self.assertEqual(r["license"], "unknown")

    def test_github(self):
        rows = lit_search.parse_github(GITHUB_JSON)
        self.assertEqual(rows[0]["license"], "MIT")
        self.assertEqual(rows[0]["id"], "gh-someone-open-insole")
        self.assertEqual(rows[1]["license"], "unknown")
        self.assertEqual(rows[1]["summary"], "")

    def test_openalex(self):
        r = lit_search.parse_openalex(OPENALEX_JSON)[0]
        self.assertEqual(r["id"], "hopper2022-validity-of-insole-derived")
        self.assertEqual(r["license"], "cc-by")
        self.assertEqual(r["url"], "https://doi.org/10.1234/abcd")

    def test_pubmed(self):
        r = lit_search.parse_pubmed_summary(PUBMED_JSON)[0]
        self.assertEqual(r["url"], "https://pubmed.ncbi.nlm.nih.gov/123/")
        self.assertEqual(r["year"], "2021")
        self.assertEqual(r["id"], "curie2021-plantar-pressure-insoles-in")

    def test_outputs(self):
        rows = lit_search.parse_github(GITHUB_JSON)
        md = lit_search.to_markdown(rows)
        self.assertIn("| 1 | `gh-someone-open-insole`", md)
        y = lit_search.to_yaml_stubs(rows)
        self.assertIn("status: candidate", y)
        try:
            import yaml  # type: ignore
        except ImportError:
            return
        parsed = yaml.safe_load(y)
        self.assertEqual(parsed[0]["title"], "someone/open-insole")


if __name__ == "__main__":
    unittest.main()
