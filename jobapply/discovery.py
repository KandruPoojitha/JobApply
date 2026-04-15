from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode

import httpx

from jobapply.config import GOOGLE_API_KEY, GOOGLE_CX


def google_custom_search(
    query: str,
    *,
    num: int = 10,
) -> list[dict[str, Any]]:
    """
    Programmable Google Custom Search JSON API.
    Requires GOOGLE_API_KEY and GOOGLE_CX (search engine id) in .env.
    Create a Programmable Search Engine at https://programmablesearchengine.google.com/
    and enable the Custom Search JSON API in Google Cloud Console.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        raise RuntimeError(
            "Set GOOGLE_API_KEY and GOOGLE_CX in .env to use Google job search."
        )
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": min(num, 10),
    }
    url = "https://www.googleapis.com/customsearch/v1?" + urlencode(params)
    r = httpx.get(url, timeout=30.0)
    r.raise_for_status()
    data = r.json()
    items = data.get("items") or []
    out: list[dict[str, Any]] = []
    for it in items:
        out.append(
            {
                "title": it.get("title"),
                "link": it.get("link"),
                "snippet": it.get("snippet"),
            }
        )
    return out


def indeed_search_placeholder() -> str:
    """Indeed does not offer a simple public job-search API for personal scripts."""
    return json.dumps(
        {
            "message": (
                "Indeed's official APIs are partner-oriented. For MVP, paste job URLs "
                "or use Google Custom Search with site:indeed.com in your query."
            ),
            "next_steps": [
                "Use the Google Custom Search integration in this app once GOOGLE_API_KEY and GOOGLE_CX are set.",
                "Or add jobs manually from Indeed in the Streamlit form.",
            ],
        },
        indent=2,
    )
