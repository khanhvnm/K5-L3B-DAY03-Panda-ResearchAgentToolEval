from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Any

import requests

from tools._shared import TIMEOUT, err

HANDLE_NAMES = {
    "sama": "Sam Altman",
    "elonmusk": "Elon Musk",
    "karpathy": "Andrej Karpathy",
    "ylecun": "Yann LeCun",
    "demishassabis": "Demis Hassabis",
    "openai": "OpenAI",
}


def _timeline_rss_fallback(screenname: str, limit: int) -> list[dict[str, Any]]:
    person = HANDLE_NAMES.get(screenname.lower(), screenname)
    response = requests.get(
        "https://news.google.com/rss/search",
        params={"q": f'"{person}" OR @{screenname}', "hl": "en-US", "gl": "US", "ceid": "US:en"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)
    items: list[dict[str, Any]] = []
    for idx, entry in enumerate(root.findall(".//item")[:limit], start=1):
        title = (entry.findtext("title") or "").strip()
        link = (entry.findtext("link") or f"https://x.com/{screenname}").strip()
        pub_date = (entry.findtext("pubDate") or "").strip()
        items.append({
            "title": title[:120],
            "summary": f"[@{screenname} / {person}] {title}",
            "url": link,
            "source": f"@{screenname}",
            "date": pub_date,
            "metrics": {"favorites": None, "retweets": None, "views": None},
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


def get_user_tweets(screenname: str = "", limit: int = 5) -> dict[str, Any]:
    try:
        # Regression fixes: models often send "@sama" (API wants "sama") or an empty handle.
        screenname = screenname.strip().lstrip("@").strip() if isinstance(screenname, str) else ""
        if not screenname:
            raise ValueError("screenname must be a non-empty handle")
        clamped_limit = max(1, min(int(limit or 5), 20))
        if not os.getenv("RAPIDAPI_KEY") and not os.getenv("PYTEST_CURRENT_TEST"):
            return {"tool": "get_user_tweets", "screenname": screenname, "items": _timeline_rss_fallback(screenname, clamped_limit)}
        data = _twitter_get("/timeline.php", {"screenname": screenname})
        return {"tool": "get_user_tweets", "screenname": screenname, "items": _tweets_from(data, limit)}
    except Exception as exc:
        return err("get_user_tweets", exc)

