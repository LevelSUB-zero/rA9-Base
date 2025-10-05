from __future__ import annotations

from typing import List, Tuple

try:
    from duckduckgo_search import DDGS
except Exception:  # pragma: no cover
    DDGS = None  # type: ignore


def web_search_snippets(query: str, max_results: int = 3) -> List[Tuple[str, str]]:
    if DDGS is None:
        return []
    results: List[Tuple[str, str]] = []
    with DDGS() as ddgs:  # type: ignore
        for r in ddgs.text(query, max_results=max_results):
            url = r.get("href") or r.get("url") or ""
            snippet = r.get("body") or r.get("snippet") or ""
            if url and snippet:
                results.append((url, snippet))
    return results


