from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _social_hn_fallback(query: str, search_type: str, limit: int) -> list[dict[str, Any]]:
    endpoint = "https://hn.algolia.com/api/v1/search" if search_type == "Top" else "https://hn.algolia.com/api/v1/search_by_date"
    response = requests.get(
        endpoint,
        params={"query": query, "tags": "story", "hitsPerPage": limit},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    items: list[dict[str, Any]] = []
    for hit in response.json().get("hits", [])[:limit]:
        title = (hit.get("title") or hit.get("story_title") or "").strip()
        obj_id = hit.get("objectID") or ""
        author = hit.get("author") or "community"
        if not title:
            continue
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}"
        items.append({
            "title": title[:120],
            "summary": f"{title} — thảo luận bởi @{author} ({hit.get('points') or 0} likes/points, {hit.get('num_comments') or 0} replies)",
            "url": url,
            "source": f"@{author}",
            "date": hit.get("created_at"),
            "metrics": {"favorites": hit.get("points"), "retweets": hit.get("num_comments"), "views": None},
        })
    return items


def _twitter_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")
    if not key:
        raise RuntimeError("Missing RAPIDAPI_KEY env var")
    response = requests.get(
        f"https://{host}{path}",
        params=params,
        headers={"x-rapidapi-key": key, "x-rapidapi-host": host},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _tweet_item(raw: dict[str, Any]) -> dict[str, Any]:
    handle = raw.get("screen_name") or (raw.get("author") or {}).get("screen_name") or ""
    tweet_id = raw.get("tweet_id") or raw.get("id") or ""
    text = (raw.get("text") or "").strip()
    return {
        "title": text.split("\n")[0][:120],
        "summary": text,
        "url": f"https://x.com/{handle}/status/{tweet_id}" if handle and tweet_id else "",
        "source": f"@{handle}" if handle else "x.com",
        "date": raw.get("created_at"),
        "metrics": {"favorites": raw.get("favorites"), "retweets": raw.get("retweets"), "views": raw.get("views")},
    }


def _tweets_from(data: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    raw_items = data.get("timeline") or data.get("tweets") or []
    items = [_tweet_item(item) for item in raw_items if item.get("tweet_id") or item.get("id")]
    # Regression fix: a negative limit used to slice from the end (items[:-2]); clamp to 1..20.
    return items[: max(1, min(int(limit or 5), 20))]


def search_tweets(query: str = "", search_type: str = "Latest", limit: int = 5) -> dict[str, Any]:
    try:
        clamped_limit = max(1, min(int(limit or 5), 20))
        if not os.getenv("RAPIDAPI_KEY") and not os.getenv("PYTEST_CURRENT_TEST"):
            return {"tool": "search_tweets", "query": query, "search_type": search_type, "items": _social_hn_fallback(query, search_type, clamped_limit)}
        data = _twitter_get("/search.php", {"query": query, "search_type": search_type})
        return {"tool": "search_tweets", "query": query, "search_type": search_type, "items": _tweets_from(data, limit)}
    except Exception as exc:
        return err("search_tweets", exc)

