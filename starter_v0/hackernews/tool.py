from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HN_SEARCH_BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"
MAX_LIMIT = 20


def _clamp_limit(limit: Any, default: int = 5) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        return default
    return max(1, min(value, MAX_LIMIT))


def search_hackernews(query: str = "", sort_by: str = "relevance", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News stories through the free Algolia API (no API key)."""
    try:
        query = (query or "").strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query must be a non-empty string")
        sort_by = sort_by if sort_by in {"relevance", "date"} else "relevance"
        limit = _clamp_limit(limit)
        response = requests.get(
            HN_SEARCH_BY_DATE_URL if sort_by == "date" else HN_SEARCH_URL,
            params={"query": query, "tags": "story", "hitsPerPage": limit},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items: list[dict[str, Any]] = []
        for hit in response.json().get("hits", []):
            object_id = hit.get("objectID")
            title = hit.get("title") or hit.get("story_title")
            if not object_id or not title:
                continue
            discussion_url = f"https://news.ycombinator.com/item?id={object_id}"
            items.append({
                "title": title,
                "url": hit.get("url") or discussion_url,
                "discussion_url": discussion_url,
                "source": "news.ycombinator.com",
                "summary": f"{hit.get('points') or 0} points, {hit.get('num_comments') or 0} comments, by {hit.get('author') or 'unknown'}",
                "date": hit.get("created_at"),
                "metrics": {"points": hit.get("points"), "comments": hit.get("num_comments")},
            })
        return {"tool": "search_hackernews", "query": query, "sort_by": sort_by, "items": items[:limit]}
    except Exception as exc:
        return err("search_hackernews", exc)
