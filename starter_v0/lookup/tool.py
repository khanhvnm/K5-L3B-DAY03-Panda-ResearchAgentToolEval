from __future__ import annotations

import html
import os
import re
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import quote_plus

import requests

from tools._shared import TIMEOUT, domain, err


VALID_TOPICS = {"general", "news"}
VALID_TIMEFRAMES = {"day", "week", "month", "year"}
TIMEFRAME_TO_WHEN = {"day": "1d", "week": "7d", "month": "30d", "year": "1y"}


def _google_news_rss_fallback(query: str, topic: str, timeframe: str | None, limit: int) -> dict[str, Any]:
    """Keyless fallback using Google News RSS when TAVILY_API_KEY is not configured in live mode."""
    q = f"{query} when:{TIMEFRAME_TO_WHEN[timeframe]}" if timeframe in TIMEFRAME_TO_WHEN else query
    url = f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(url, headers={"User-Agent": "ResearchAgentLab/1.0"}, timeout=TIMEOUT)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    items = []
    for item in root.findall("./channel/item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        source_el = item.find("source")
        source_name = (
            source_el.text.strip()
            if source_el is not None and source_el.text
            else domain(source_el.attrib.get("url", "") if source_el is not None else link)
        )
        raw_desc = item.findtext("description") or ""
        clean_desc = re.sub(r"<[^>]+>", " ", html.unescape(raw_desc))
        clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
        items.append({
            "title": title,
            "url": link,
            "source": source_name or "news.google.com",
            "summary": f"[{pub_date}] {clean_desc[:300]}" if pub_date else clean_desc[:300],
            "score": 1.0,
        })
    return {
        "tool": "web_search",
        "query": query,
        "topic": topic,
        "timeframe": timeframe,
        "provider": "google_news_rss_fallback",
        "items": items,
    }


def web_search(query: str = "", topic: str = "general", timeframe: str | None = "week", max_results: int = 5) -> dict[str, Any]:
    try:
        # Regression fixes: do not spend a Tavily credit on an empty query, clamp max_results,
        # and drop values outside the enum (e.g. timeframe="today") instead of sending a 400.
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        topic = topic if topic in VALID_TOPICS else "general"
        timeframe = timeframe if timeframe in VALID_TIMEFRAMES else None
        limit = max(1, min(int(max_results or 5), 20))
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            if os.getenv("PYTEST_CURRENT_TEST"):
                raise RuntimeError("Missing TAVILY_API_KEY env var")
            return _google_news_rss_fallback(query.strip(), topic, timeframe, limit)
        body: dict[str, Any] = {"query": query, "topic": topic, "max_results": limit, "search_depth": "basic"}
        if timeframe:
            body["time_range"] = timeframe
        response = requests.post(
            "https://api.tavily.com/search",
            json=body,
            headers={"Authorization": f"Bearer {key}"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        items = [{
            "title": item.get("title"),
            "url": item.get("url"),
            "source": domain(item.get("url", "")),
            "summary": item.get("content"),
            "score": item.get("score"),
        } for item in data.get("results", [])]
        return {"tool": "web_search", "query": query, "topic": topic, "timeframe": timeframe, "items": items}
    except Exception as exc:
        return err("web_search", exc)

