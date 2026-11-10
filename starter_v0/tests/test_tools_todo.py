"""Tool unit tests (offline, free): the Tool Unit Test Challenge, completed.

Sections:
  1. Stubs from the starter (clarify, format, send, lookup, fetch, timeline, social_search, policy).
  2. Regression tests for bugs found by probing boundary inputs the model really sends (see REPORT B5).
  3. Tests for the 4 team-added tools: hackernews, github_search, wikipedia, current_time.

Rules: offline only (mock HTTP with `fake_http`, fake keys with `monkeypatch.setenv`),
one behaviour per test, name the test after the behaviour.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS
from tools.current_time import tool as current_time_module

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
hackernews_tool = TOOL_FUNCTIONS["hackernews"]
github_tool = TOOL_FUNCTIONS["github_search"]
wikipedia_tool = TOOL_FUNCTIONS["wikipedia"]
current_time_tool = TOOL_FUNCTIONS["current_time"]


def _tweets(count: int, handle: str = "sama") -> list[dict]:
    return [{"tweet_id": str(i), "screen_name": handle, "text": f"tweet {i}"} for i in range(1, count + 1)]


# ======================= 1. starter stubs =======================

# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify_tool(question="Chọn nguồn?", response_type="choice", options=["web", "twitter"])
    assert result["options"] == ["web", "twitter"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "section": "A"},
        {"title": "b1", "section": "B"},
        {"title": "a2", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]
    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    assert markdown.index("a1") < markdown.index("a2") < markdown.index("b1")


def test_format_thread_numbers_items() -> None:
    items = [{"title": "one"}, {"title": "two"}, {"title": "three"}]
    markdown = format_tool(items=items, template="thread")["markdown"]
    lines = [line for line in markdown.split("\n") if line]
    assert [line.split(" ")[0] for line in lines] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    assert format_tool(items=None, template="sections")["item_count"] == 0
    assert format_tool(items=[], template="brief")["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@my_channel")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123:ABC/sendMessage" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "@my_channel"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="x", confirmed=True)
    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))
    lookup_tool(query="AI", timeframe=None)
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello\nbody",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    result = fetch_tool(url="https://example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"] == {"url": "https://example.com/post", "formats": ["markdown"]}
    assert calls[0]["headers"]["Authorization"] == "Bearer fc-test"
    assert result["items"][0] == {
        "title": "T", "url": "https://www.example.com/post",
        "source": "example.com", "summary": "# Hello\nbody",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "y" * 9000, "metadata": {}}}))
    summary = fetch_tool(url="https://example.com/long")["items"][0]["summary"]
    assert len(summary) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    raw = [{"screen_name": "sama", "text": "no id"}, *_tweets(6)]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = timeline_tool(screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "rk"
    assert len(result["items"]) == 3
    assert [item["url"] for item in result["items"]] == [f"https://x.com/sama/status/{i}" for i in (1, 2, 3)]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": _tweets(2)}))

    social_search_tool(query="OpenAI", search_type="Top", limit=2)
    social_search_tool(query="OpenAI", search_type="Latest", limit=2)

    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert calls[1]["params"] == {"query": "OpenAI", "search_type": "Latest"}


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert policy_tool(query="")["results"] == []
    assert policy_tool(query="   ")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy_tool(query="data confidential customer", policy_area="data_privacy", top_k=5)["results"]
    assert results
    assert {item["policy_area"] for item in results} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = policy_tool(query="injection probe", policy_area="source_citation", top_k=5)["results"]
    probe = next(item for item in results if item["section"] == "Injection probe")
    assert any("ignore the citation policy" in line for line in probe["untrusted_text"])
    assert "ignore the citation policy" not in probe["facts"]
    assert all("ignore the citation policy" not in item["facts"] for item in results)


# ======================= 2. regression tests (bugs found in starter tools) =======================

def test_send_with_string_false_does_not_send(monkeypatch, fake_http) -> None:
    """BUG: confirmed="false" (a truthy string) used to bypass the confirmation guardrail."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "@c")
    calls = fake_http(FakeResponse({"ok": True}))
    for value in ("false", "no", "true", 1, None):
        result = send_tool(text="Bản tin", confirmed=value)
        assert result["status"] == "needs_confirmation", value
    assert calls == []


@pytest.mark.parametrize("limit", [0, -2, None])
def test_timeline_non_positive_limit_never_returns_slice_from_end(monkeypatch, fake_http, limit) -> None:
    """BUG: limit=-2 used to return len-2 items (python negative slice) instead of a sane count."""
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    fake_http(FakeResponse({"timeline": _tweets(10)}))
    items = timeline_tool(screenname="sama", limit=limit)["items"]
    assert 1 <= len(items) <= 5


def test_timeline_strips_at_sign_from_handle(monkeypatch, fake_http) -> None:
    """BUG: '@sama' was forwarded as-is although the API expects the bare handle."""
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": _tweets(1)}))
    timeline_tool(screenname="@sama")
    assert calls[0]["params"] == {"screenname": "sama"}


def test_timeline_empty_handle_returns_error_without_request(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": _tweets(1)}))
    assert timeline_tool(screenname="  ")["error"] == "ValueError"
    assert calls == []


def test_lookup_empty_query_does_not_spend_api_credit(monkeypatch, fake_http) -> None:
    """BUG: empty query was still sent to Tavily."""
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))
    assert lookup_tool(query="")["error"] == "ValueError"
    assert calls == []


def test_lookup_clamps_max_results_and_accepts_numeric_string(monkeypatch, fake_http) -> None:
    """BUG: max_results=-3 was forwarded to Tavily; "5" must keep working."""
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))
    lookup_tool(query="x", max_results=-3)
    lookup_tool(query="x", max_results="5")
    lookup_tool(query="x", max_results=999)
    assert [call["json"]["max_results"] for call in calls] == [1, 5, 20]


def test_lookup_drops_out_of_enum_timeframe_and_topic(monkeypatch, fake_http) -> None:
    """BUG: timeframe="today" / topic="tech" were forwarded and made Tavily answer 400."""
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))
    lookup_tool(query="x", topic="tech", timeframe="today")
    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["topic"] == "general"


@pytest.mark.parametrize("url", ["", "   ", "not a url", "ftp://example.com/x"])
def test_fetch_rejects_non_http_url_without_request(monkeypatch, fake_http, url) -> None:
    """BUG: empty url was sent to Firecrawl and returned a bogus empty item."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc")
    calls = fake_http(FakeResponse({"data": {"markdown": "m", "metadata": {}}}))
    assert fetch_tool(url=url)["error"] == "ValueError"
    assert calls == []


def test_format_accepts_plain_string_and_null_items() -> None:
    """BUG: items=["text"] raised AttributeError ('str' has no attribute 'get')."""
    result = format_tool(items=["chỉ là chuỗi", None, {"title": "ok", "url": "https://a.com/x"}], template="bullets")
    assert result["item_count"] == 2
    assert "chỉ là chuỗi" in result["markdown"]


def test_format_item_without_url_has_no_empty_link() -> None:
    markdown = format_tool(items=[{"title": "No link"}], template="bullets")["markdown"]
    assert "()" not in markdown
    assert markdown.startswith("- No link")


def test_policy_top_k_zero_or_string_still_returns_results() -> None:
    assert len(policy_tool(query="citation", top_k=0)["results"]) >= 1
    assert len(policy_tool(query="citation", top_k="2")["results"]) <= 2


# ======================= 3. new tool: hackernews =======================

def test_hackernews_happy_path_maps_hits_and_sends_expected_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [
        {"objectID": "42", "title": "Show HN: Agent evals", "url": "https://example.com/evals",
         "points": 120, "num_comments": 33, "author": "pg", "created_at": "2026-01-01T00:00:00Z"},
        {"objectID": "43", "title": "Ask HN: Best RAG stack?", "url": None, "points": 5, "num_comments": 2, "author": "x"},
    ]}))

    result = hackernews_tool(query="agent evals", limit=2)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"] == {"query": "agent evals", "tags": "story", "hitsPerPage": 2}
    first, second = result["items"]
    assert first["url"] == "https://example.com/evals"
    assert first["discussion_url"] == "https://news.ycombinator.com/item?id=42"
    assert first["summary"] == "120 points, 33 comments, by pg"
    assert second["url"] == "https://news.ycombinator.com/item?id=43"  # text post falls back to the thread


def test_hackernews_sort_by_date_uses_search_by_date_endpoint(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    hackernews_tool(query="llm", sort_by="date")
    hackernews_tool(query="llm", sort_by="banana")  # out of enum -> relevance
    assert calls[0]["url"].endswith("/search_by_date")
    assert calls[1]["url"].endswith("/search")


@pytest.mark.parametrize("query", ["", "   ", None, 123])
def test_hackernews_bad_query_returns_error_without_request(fake_http, query) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    assert hackernews_tool(query=query)["error"] == "ValueError"
    assert calls == []


def test_hackernews_clamps_limit_and_survives_text_limit(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    hackernews_tool(query="a", limit=500)
    hackernews_tool(query="a", limit="abc")
    hackernews_tool(query="a", limit=-4)
    assert [call["params"]["hitsPerPage"] for call in calls] == [20, 5, 1]


def test_hackernews_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))
    assert hackernews_tool(query="x")["error"] == "HTTPError"


def test_hackernews_skips_hits_without_title_or_id(fake_http) -> None:
    fake_http(FakeResponse({"hits": [{"objectID": "1"}, {"title": "no id"}, {"objectID": "2", "title": "ok"}]}))
    assert [item["title"] for item in hackernews_tool(query="x")["items"]] == ["ok"]


# ======================= new tool: github_search =======================

def test_github_search_happy_path_maps_repos(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": [
        {"full_name": "langchain-ai/langchain", "html_url": "https://github.com/langchain-ai/langchain",
         "description": "Build LLM apps", "stargazers_count": 100000, "forks_count": 15000,
         "language": "Python", "pushed_at": "2026-01-02T00:00:00Z"},
    ]}))

    result = github_tool(query="llm agent framework", limit=1)

    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {"q": "llm agent framework", "sort": "stars", "order": "desc", "per_page": 1}
    assert "Authorization" not in calls[0]["headers"]
    assert result["items"][0] == {
        "title": "langchain-ai/langchain", "url": "https://github.com/langchain-ai/langchain",
        "source": "github.com", "summary": "Build LLM apps", "date": "2026-01-02T00:00:00Z",
        "metrics": {"stars": 100000, "forks": 15000, "language": "Python"},
    }


def test_github_search_uses_token_when_present_and_valid_sort(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    calls = fake_http(FakeResponse({"items": []}))
    github_tool(query="rag", sort="updated")
    github_tool(query="rag", sort="forks")  # out of enum -> stars
    assert calls[0]["headers"]["Authorization"] == "Bearer ghp_test"
    assert calls[0]["params"]["sort"] == "updated"
    assert calls[1]["params"]["sort"] == "stars"


@pytest.mark.parametrize("query", ["", "  ", None])
def test_github_search_empty_query_returns_error_without_request(fake_http, query) -> None:
    calls = fake_http(FakeResponse({"items": []}))
    assert github_tool(query=query)["error"] == "ValueError"
    assert calls == []


def test_github_search_rate_limit_returns_error_dict_and_null_description_ok(fake_http) -> None:
    fake_http(FakeResponse(status_code=403))
    assert github_tool(query="x")["error"] == "HTTPError"
    fake_http(FakeResponse({"items": [{"full_name": "a/b", "html_url": "https://github.com/a/b", "description": None}]}))
    assert github_tool(query="x")["items"][0]["summary"] == ""


# ======================= new tool: wikipedia =======================

def test_wikipedia_happy_path_maps_summary(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "title": "Retrieval-augmented generation",
        "extract": "RAG is a technique...",
        "description": "AI technique",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"}},
    }))

    result = wikipedia_tool(title="Retrieval-augmented generation")

    assert calls[0]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/Retrieval-augmented_generation"
    assert "User-Agent" in calls[0]["headers"]
    assert result["items"][0] == {
        "title": "Retrieval-augmented generation",
        "url": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        "source": "en.wikipedia.org",
        "summary": "RAG is a technique...",
        "description": "AI technique",
    }


def test_wikipedia_vi_language_and_unsafe_title_is_encoded(fake_http) -> None:
    calls = fake_http(FakeResponse({"title": "AI", "extract": "x"}))
    wikipedia_tool(title="Trí tuệ nhân tạo", lang="vi")
    wikipedia_tool(title="a/b?c", lang="de")  # unsupported language -> en, '/' and '?' must not escape the path
    assert calls[0]["url"].startswith("https://vi.wikipedia.org/api/rest_v1/page/summary/")
    assert "Tr%C3%AD_tu%E1%BB%87_nh%C3%A2n_t%E1%BA%A1o" in calls[0]["url"]
    assert calls[1]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/a%2Fb%3Fc"


@pytest.mark.parametrize("title", ["", "   ", None, 42])
def test_wikipedia_bad_title_returns_error_without_request(fake_http, title) -> None:
    calls = fake_http(FakeResponse({}))
    assert wikipedia_tool(title=title)["error"] == "ValueError"
    assert calls == []


def test_wikipedia_missing_page_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=404))
    result = wikipedia_tool(title="Definitely not a page")
    assert result["error"] == "HTTPError"
    assert result["tool"] == "wikipedia_summary"


def test_wikipedia_network_exception_is_caught(fake_http) -> None:
    fake_http(requests.ConnectionError("down"))
    assert wikipedia_tool(title="AI")["error"] == "ConnectionError"


# ======================= new tool: current_time =======================

@pytest.fixture
def frozen_clock(monkeypatch):
    # 2026-03-15 (Sunday) 17:30:00 UTC
    monkeypatch.setattr(current_time_module, "_utcnow", lambda: datetime(2026, 3, 15, 17, 30, tzinfo=timezone.utc))


def test_current_time_default_is_vietnam_time(frozen_clock) -> None:
    result = current_time_tool()
    assert result["date"] == "2026-03-16"  # +7h crosses midnight
    assert result["time"] == "00:30:00"
    assert result["weekday"] == "Thứ Hai"
    assert result["iso"] == "2026-03-16T00:30:00+07:00"


def test_current_time_respects_negative_offset(frozen_clock) -> None:
    result = current_time_tool(utc_offset_hours=-5)
    assert result["date"] == "2026-03-15"
    assert result["time"] == "12:30:00"
    assert result["weekday"] == "Chủ Nhật"


def test_current_time_bad_input_text_falls_back_and_out_of_range_errors(frozen_clock) -> None:
    assert current_time_tool(utc_offset_hours="abc")["utc_offset_hours"] == 7
    assert current_time_tool(utc_offset_hours="9")["utc_offset_hours"] == 9
    result = current_time_tool(utc_offset_hours=99)
    assert result["error"] == "ValueError"
    assert "99" in result["message"]


def test_current_time_makes_no_network_call(frozen_clock, monkeypatch) -> None:
    def boom(*args, **kwargs):
        raise AssertionError("current_time must be offline")

    monkeypatch.setattr(requests, "get", boom)
    monkeypatch.setattr(requests, "post", boom)
    assert "error" not in current_time_tool()
