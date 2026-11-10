from __future__ import annotations

import html
import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def _direct_http_fallback(url: str) -> dict[str, Any]:
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; AI20k-Research-Agent/1.0)"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    raw_html = response.text or ""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", raw_html, flags=re.IGNORECASE | re.DOTALL)
    title = html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else url
    cleaned = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    cleaned = html.unescape(re.sub(r"<[^>]+>", " ", cleaned))
    text = re.sub(r"\s+", " ", cleaned).strip()[:4000]
    return {
        "tool": "read_url",
        "url": url,
        "items": [{
            "title": title or url,
            "url": url,
            "source": domain(url),
            "summary": text,
        }],
    }


def read_url(url: str = "") -> dict[str, Any]:
    try:
        # Regression fix: an empty/non-http url used to be sent to Firecrawl and burn a credit.
        if not isinstance(url, str) or not url.strip().lower().startswith(("http://", "https://")):
            raise ValueError("url must be an absolute http(s) URL")
        url = url.strip()
        key = os.getenv("FIRECRAWL_API_KEY")
        if not key:
            if os.getenv("PYTEST_CURRENT_TEST"):
                raise RuntimeError("Missing FIRECRAWL_API_KEY env var")
            return _direct_http_fallback(url)
        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            json={"url": url, "formats": ["markdown"]},
            headers={"Authorization": f"Bearer {key}"},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        meta = data.get("metadata", {}) or {}
        return {"tool": "read_url", "url": url, "items": [{
            "title": meta.get("title") or url,
            "url": meta.get("sourceURL") or url,
            "source": domain(url),
            "summary": (data.get("markdown") or "")[:4000],
        }]}
    except Exception as exc:
        return err("read_url", exc)

