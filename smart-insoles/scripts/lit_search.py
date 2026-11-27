#!/usr/bin/env python3
"""Search helpers for the research-scout. Standard library only.

    python3 scripts/lit_search.py github   "smart insole gait"   [--limit 10] [--yaml]
    python3 scripts/lit_search.py arxiv    "insole running gait"
    python3 scripts/lit_search.py openalex "plantar pressure insole running"
    python3 scripts/lit_search.py pubmed   "instrumented insole ground contact time"

Output is a Markdown table, or with --yaml, `research/sources.yaml` stubs (status: candidate).
Results are LEADS, not verified sources. Open each URL before registering it, and never copy a
licence from this output without checking the LICENSE file or the paper itself.

Optional environment variables (never required):
  GITHUB_TOKEN    raises GitHub's rate limit
  OPENALEX_MAILTO joins OpenAlex's "polite pool" (set it yourself; agents must not invent one)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List

USER_AGENT = "smart-insoles-harness/0.1 (research helper)"
TIMEOUT = 30


def _get(url: str, headers: Dict[str, str] | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310 - fixed https hosts
        return resp.read()


def _slug(text: str, max_words: int = 5) -> str:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return "-".join(words[:max_words]) or "untitled"


# ---------------------------------------------------------------- parsers (pure, unit-tested)


def parse_github(payload: dict) -> List[dict]:
    out = []
    for item in payload.get("items", []):
        lic = (item.get("license") or {}).get("spdx_id") or "unknown"
        out.append(
            {
                "id": f"gh-{_slug(item.get('full_name', ''), 6)}",
                "type": "repo",
                "title": item.get("full_name", ""),
                "url": item.get("html_url", ""),
                "year": (item.get("pushed_at") or "")[:4],
                "license": "unknown" if lic in ("NOASSERTION", "") else lic,
                "extra": f"★{item.get('stargazers_count', 0)} · pushed {(item.get('pushed_at') or '')[:10]}",
                "summary": (item.get("description") or "").strip(),
            }
        )
    return out


ATOM = "{http://www.w3.org/2005/Atom}"


def parse_arxiv(xml_bytes: bytes) -> List[dict]:
    root = ET.fromstring(xml_bytes)
    out = []
    for entry in root.findall(f"{ATOM}entry"):
        title = " ".join((entry.findtext(f"{ATOM}title") or "").split())
        authors = [a.findtext(f"{ATOM}name") or "" for a in entry.findall(f"{ATOM}author")]
        url = entry.findtext(f"{ATOM}id") or ""
        year = (entry.findtext(f"{ATOM}published") or "")[:4]
        first = authors[0].split()[-1].lower() if authors else "anon"
        out.append(
            {
                "id": f"{first}{year}-{_slug(title, 4)}",
                "type": "paper",
                "title": title,
                "url": url,
                "year": year,
                "license": "unknown",
                "extra": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
                "summary": " ".join((entry.findtext(f"{ATOM}summary") or "").split())[:240],
            }
        )
    return out


def parse_openalex(payload: dict) -> List[dict]:
    out = []
    for w in payload.get("results", []):
        authors = [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])]
        title = w.get("display_name") or w.get("title") or ""
        year = str(w.get("publication_year") or "")
        first = authors[0].split()[-1].lower() if authors and authors[0] else "anon"
        oa = w.get("open_access") or {}
        loc = w.get("primary_location") or {}
        lic = loc.get("license") or "paper-copyright"
        out.append(
            {
                "id": f"{first}{year}-{_slug(title, 4)}",
                "type": "paper",
                "title": title,
                "url": w.get("doi") or w.get("id", ""),
                "year": year,
                "license": lic,
                "extra": f"cited {w.get('cited_by_count', 0)} · OA {oa.get('oa_status', '?')}",
                "summary": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
            }
        )
    return out


def parse_pubmed_summary(payload: dict) -> List[dict]:
    result = payload.get("result", {})
    out = []
    for uid in result.get("uids", []):
        doc = result.get(uid, {})
        title = doc.get("title", "").rstrip(".")
        year = (doc.get("pubdate") or "")[:4]
        authors = [a.get("name", "") for a in doc.get("authors", [])]
        first = authors[0].split()[0].lower() if authors else "anon"
        out.append(
            {
                "id": f"{first}{year}-{_slug(title, 4)}",
                "type": "paper",
                "title": title,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                "year": year,
                "license": "paper-copyright",
                "extra": f"{doc.get('source', '')} · PMID {uid}",
                "summary": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
            }
        )
    return out


# ---------------------------------------------------------------- fetchers


def search_github(query: str, limit: int) -> List[dict]:
    q = urllib.parse.urlencode({"q": query, "per_page": limit, "sort": "stars"})
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    return parse_github(json.loads(_get(f"https://api.github.com/search/repositories?{q}", headers)))


def search_arxiv(query: str, limit: int) -> List[dict]:
    q = urllib.parse.urlencode({"search_query": f"all:{query}", "max_results": limit})
    return parse_arxiv(_get(f"https://export.arxiv.org/api/query?{q}"))


def search_openalex(query: str, limit: int) -> List[dict]:
    params = {"search": query, "per-page": limit}
    if os.environ.get("OPENALEX_MAILTO"):
        params["mailto"] = os.environ["OPENALEX_MAILTO"]
    return parse_openalex(json.loads(_get(f"https://api.openalex.org/works?{urllib.parse.urlencode(params)}")))


def search_pubmed(query: str, limit: int) -> List[dict]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    ids = json.loads(
        _get(f"{base}/esearch.fcgi?{urllib.parse.urlencode({'db': 'pubmed', 'term': query, 'retmax': limit, 'retmode': 'json'})}")
    )["esearchresult"]["idlist"]
    if not ids:
        return []
    summary = json.loads(
        _get(f"{base}/esummary.fcgi?{urllib.parse.urlencode({'db': 'pubmed', 'id': ','.join(ids), 'retmode': 'json'})}")
    )
    return parse_pubmed_summary(summary)


# ---------------------------------------------------------------- output


def to_markdown(rows: List[dict]) -> str:
    lines = ["| # | id (suggested) | title | year | licence (UNVERIFIED) | info | url |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        title = r["title"].replace("|", "/")[:90]
        lines.append(f"| {i} | `{r['id']}` | {title} | {r['year']} | {r['license']} | {r['extra']} | {r['url']} |")
    return "\n".join(lines)


def to_yaml_stubs(rows: List[dict]) -> str:
    def q(s: str) -> str:
        return json.dumps(s, ensure_ascii=False)  # JSON strings are valid YAML scalars

    out = ["# UNVERIFIED stubs: open each URL, confirm title/authors/licence, then add `verified: <date>`"]
    for r in rows:
        out += [
            f"- id: {r['id']}",
            f"  type: {r['type']}",
            f"  title: {q(r['title'])}",
            f"  url: {r['url']}",
            f"  year: {r['year'] or 'unknown'}",
            f"  license: {r['license']}",
            "  status: candidate",
            f"  summary: {q(r['summary'][:200])}",
        ]
    return "\n".join(out)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", choices=["github", "arxiv", "openalex", "pubmed"])
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--yaml", action="store_true", help="emit sources.yaml stubs instead of a table")
    args = parser.parse_args(argv)
    fn = {"github": search_github, "arxiv": search_arxiv, "openalex": search_openalex, "pubmed": search_pubmed}[args.source]
    try:
        rows = fn(args.query, max(1, min(args.limit, 50)))
    except Exception as exc:  # noqa: BLE001
        print(f"search failed ({args.source}): {exc}. Fall back to WebSearch/WebFetch.", file=sys.stderr)
        return 2
    print(to_yaml_stubs(rows) if args.yaml else to_markdown(rows))
    print(f"\n{len(rows)} result(s) from {args.source} for {args.query!r}. These are leads, not verified sources.",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
