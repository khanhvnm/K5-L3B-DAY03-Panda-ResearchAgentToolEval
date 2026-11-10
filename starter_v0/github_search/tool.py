from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
MAX_LIMIT = 20


def _clamp_limit(limit: Any, default: int = 5) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        return default
    return max(1, min(value, MAX_LIMIT))


def search_github_repos(query: str = "", sort: str = "stars", limit: int = 5) -> dict[str, Any]:
    """Search public GitHub repositories. GITHUB_TOKEN is optional (raises the rate limit)."""
    try:
        query = (query or "").strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query must be a non-empty string")
        sort = sort if sort in {"stars", "updated"} else "stars"
        limit = _clamp_limit(limit)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI20k-Day03-Research-Agent"}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(
            GITHUB_SEARCH_URL,
            params={"q": query, "sort": sort, "order": "desc", "per_page": limit},
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items = [{
            "title": repo.get("full_name"),
            "url": repo.get("html_url"),
            "source": "github.com",
            "summary": repo.get("description") or "",
            "date": repo.get("pushed_at"),
            "metrics": {"stars": repo.get("stargazers_count"), "forks": repo.get("forks_count"), "language": repo.get("language")},
        } for repo in response.json().get("items", []) if repo.get("full_name")]
        return {"tool": "search_github_repos", "query": query, "sort": sort, "items": items[:limit]}
    except Exception as exc:
        return err("search_github_repos", exc)
