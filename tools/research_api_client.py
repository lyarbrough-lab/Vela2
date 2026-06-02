#!/usr/bin/env python3
"""
research_api_client.py — Unified research API client for Vela2.
Supports NASA ADS, Semantic Scholar, arXiv, and more.

Setup:
  1. NASA ADS: Register at https://ui.adsabs.harvard.edu/ -> Settings -> API Token
     Add to .env: NASA_ADS_API_KEY=your_token_here
  
  2. Semantic Scholar: (optional) Apply for free key at:
     https://www.semanticscholar.org/product/api#api-key-form
     Add to .env: SEMANTIC_SCHOLAR_API_KEY=your_key_here
  
  3. arXiv: No key needed. Free and open.
"""

import os
import requests
from datetime import datetime, timezone
import feedparser  # for arXiv XML parsing

# ── Globals ──
REQUEST_TIMEOUT = 30  # seconds — prevents hanging on stalled APIs

# ── Load API keys from environment ──
NASA_ADS_KEY = os.environ.get("NASA_ADS_API_KEY", "")
SEMANTIC_SCHOLAR_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

# ── NASA ADS ──
ADS_BASE = "https://api.adsabs.harvard.edu/v1"

def _safe_get(url, params=None, headers=None, timeout=REQUEST_TIMEOUT):
    """GET with timeout + structured error handling. Returns parsed JSON or error dict."""
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.Timeout:
        return {"error": f"Request timed out after {timeout}s", "endpoint": url}
    except requests.ConnectionError:
        return {"error": "Connection failed — check network or endpoint URL", "endpoint": url}
    except requests.HTTPError as e:
        return {"error": f"HTTP {resp.status_code}: {resp.reason}", "endpoint": url}
    except Exception as e:
        return {"error": str(e), "endpoint": url}

def ads_search(query, rows=10, fields=None):
    """Search NASA ADS. Requires NASA_ADS_API_KEY in .env"""
    if not NASA_ADS_KEY:
        return {"error": "NASA_ADS_API_KEY not set. Register at https://ui.adsabs.harvard.edu/"}
    
    if fields is None:
        fields = ["title", "author", "year", "bibcode", "citation_count", "abstract"]
    
    params = {"q": query, "fl": ",".join(fields), "rows": rows}
    headers = {"Authorization": f"Bearer {NASA_ADS_KEY}"}
    return _safe_get(f"{ADS_BASE}/search/query", params=params, headers=headers)

def ads_citations(bibcode, rows=20):
    """Get papers that cite a given bibcode."""
    if not NASA_ADS_KEY:
        return {"error": "NASA_ADS_API_KEY not set"}
    headers = {"Authorization": f"Bearer {NASA_ADS_KEY}"}
    return _safe_get(f"{ADS_BASE}/search/query",
                     params={"q": f"citations(bibcode:{bibcode})", "rows": rows},
                     headers=headers)

def ads_references(bibcode, rows=20):
    """Get references for a given bibcode."""
    if not NASA_ADS_KEY:
        return {"error": "NASA_ADS_API_KEY not set"}
    headers = {"Authorization": f"Bearer {NASA_ADS_KEY}"}
    return _safe_get(f"{ADS_BASE}/search/query",
                     params={"q": f"references(bibcode:{bibcode})", "rows": rows},
                     headers=headers)

# ── Semantic Scholar ──
S2_BASE = "https://api.semanticscholar.org/graph/v1"

def s2_search(query, limit=10, fields=None):
    """Search Semantic Scholar. Free tier works without key (limited rate)."""
    if fields is None:
        fields = ["title", "authors", "year", "externalIds", "citationCount", "abstract"]
    headers = {}
    if SEMANTIC_SCHOLAR_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_KEY
    params = {"query": query, "limit": limit, "fields": ",".join(fields)}
    return _safe_get(f"{S2_BASE}/paper/search", params=params, headers=headers)

def s2_paper_details(paper_id, fields=None):
    """Get details for a specific paper by S2 ID, arXiv ID, or DOI.
    
    Args:
        paper_id: Semantic Scholar paper ID, "arXiv:xxxx.xxxxx", or DOI (e.g. "10.1038/nature12345")
        fields: list of fields to return (defaults to title, authors, year, abstract, citationCount, references)
    """
    if fields is None:
        fields = ["title", "authors", "year", "abstract", "citationCount", "references"]
    headers = {}
    if SEMANTIC_SCHOLAR_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_KEY
    params = {"fields": ",".join(fields)}
    return _safe_get(f"{S2_BASE}/paper/{paper_id}", params=params, headers=headers)

# ── arXiv ──
ARXIV_BASE = "https://export.arxiv.org/api/query"

def arxiv_search(query, max_results=10, sort_by="relevance"):
    """Search arXiv. Free, no key needed. Returns parsed dicts (see simplify_arxiv_results)."""
    params = {"search_query": query, "max_results": max_results, "sortBy": sort_by}
    try:
        resp = requests.get(ARXIV_BASE, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return simplify_arxiv_results(resp.text)
    except requests.Timeout:
        return {"error": f"arXiv request timed out after {REQUEST_TIMEOUT}s"}
    except requests.ConnectionError:
        return {"error": "arXiv connection failed"}
    except Exception as e:
        return {"error": str(e)}

def arxiv_recent(category="astro-ph.EP", max_results=20):
    """Get recent papers from an arXiv category."""
    return arxiv_search(f"cat:{category}", max_results=max_results, sort_by="submittedDate")

def simplify_arxiv_results(raw_xml):
    """Parse arXiv Atom XML feed into clean dicts using feedparser."""
    feed = feedparser.parse(raw_xml)
    if feed.get("bozo_exception"):
        return {"error": f"Failed to parse arXiv XML: {feed.bozo_exception}"}
    results = []
    for entry in feed.entries:
        results.append({
            "title": entry.get("title", "").replace("\n", " ").strip(),
            "authors": [a.get("name", "") for a in entry.get("authors", [])],
            "published": entry.get("published"),
            "summary": (entry.get("summary", "")[:500] + "...") if entry.get("summary") else "",
            "arxiv_id": entry.get("id", "").split("/")[-1].split("v")[0] if entry.get("id") else "",
            "link": entry.get("link", ""),
            "categories": [t.get("term", "") for t in entry.get("tags", [])],
        })
    return {"results": results, "total": len(results)}

# ── Utility ──
def simplify_ads_results(raw):
    """Convert raw ADS response to a clean list of paper dicts."""
    if "error" in raw:
        return raw
    docs = raw.get("response", {}).get("docs", [])
    result = []
    for d in docs:
        result.append({
            "title": d.get("title", [""])[0],
            "authors": d.get("author", [])[:5],
            "year": d.get("year"),
            "bibcode": d.get("bibcode"),
            "citations": d.get("citation_count"),
            "abstract": (d.get("abstract", "")[:500] + "...") if d.get("abstract") else "",
        })
    return result

if __name__ == "__main__":
    print("Research API Client")
    print(f"  NASA ADS key:        {'✓' if NASA_ADS_KEY else '✗ — not set (register at ui.adsabs.harvard.edu)'}")
    print(f"  Semantic Scholar:    {'✓' if SEMANTIC_SCHOLAR_KEY else '✗ — not set (rate-limited without key)'}")
    print(f"  arXiv:               Free (no key needed)")
    print()
    print("Usage examples:")
    print("  from research_api_client import ads_search, s2_search, arxiv_search")
    print("  results = ads_search('planetary system architecture Kepler')")
    print("  results = s2_search('exoplanet resonance chain')")
    print("  feed = arxiv_recent('astro-ph.EP')")
