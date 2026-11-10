from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err

SUPPORTED_LANGS = {"en", "vi"}


def wikipedia_summary(title: str = "", lang: str = "en") -> dict[str, Any]:
    """Fetch the lead summary of one Wikipedia article (REST API, no key)."""
    try:
        title = " ".join(title.split()) if isinstance(title, str) else ""
        if not title:
            raise ValueError("title must be a non-empty string")
        lang = (lang or "en").strip().lower() if isinstance(lang, str) else "en"
        if lang not in SUPPORTED_LANGS or not re.fullmatch(r"[a-z]{2,3}", lang):
            lang = "en"
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}"
        response = requests.get(
            url,
            headers={"User-Agent": "AI20k-Day03-Research-Agent/1.0 (educational lab)", "Accept": "application/json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        page_url = ((data.get("content_urls") or {}).get("desktop") or {}).get("page") or f"https://{lang}.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
        return {
            "tool": "wikipedia_summary",
            "title": title,
            "lang": lang,
            "items": [{
                "title": data.get("title") or title,
                "url": page_url,
                "source": f"{lang}.wikipedia.org",
                "summary": data.get("extract") or "",
                "description": data.get("description") or "",
            }],
        }
    except Exception as exc:
        return err("wikipedia_summary", exc)
