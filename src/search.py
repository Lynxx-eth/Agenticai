"""Grok live-search layer.

Wraps the official `xai-sdk` Live Search API. Grok is given the researcher
system prompt and its web + X search tools, and returns raw candidate notes that
the analyzer later normalizes.
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import Settings
from .prompts import GROK_SYSTEM, grok_user_prompt


@dataclass
class SearchResult:
    notes: str          # raw research text from Grok
    citations: list[str]  # source URLs Grok actually used


def run_search(
    settings: Settings,
    niches: list[str],
    ecosystems: list[str],
    stages: list[str],
    target_count: int,
) -> SearchResult:
    """Run one research pass with whichever search engine is configured.

    Free mode (default) uses DuckDuckGo — no key needed. Set SEARCH_PROVIDER=grok
    (with a funded xAI key) to switch back to Grok's live web + X search.

    Raises a RuntimeError with a readable message on any failure so the UI can
    surface it cleanly.
    """
    if settings.search_provider == "free":
        from .free_search import run_free_search

        return run_free_search(niches, ecosystems, stages, target_count)

    return _run_grok_search(settings, niches, ecosystems, stages, target_count)


def _run_grok_search(
    settings: Settings,
    niches: list[str],
    ecosystems: list[str],
    stages: list[str],
    target_count: int,
) -> SearchResult:
    """Live web + X research with Grok (paid — needs a funded xAI key)."""
    if not settings.grok_ready:
        raise RuntimeError("xAI API key missing or malformed. Add XAI_API_KEY to your .env.")

    try:
        from xai_sdk import Client
        from xai_sdk.chat import system, user
        from xai_sdk.tools import web_search, x_search
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "xai-sdk not installed (or too old for Agent Tools). "
            "Run: pip install -U xai-sdk"
        ) from exc

    try:
        client = Client(api_key=settings.xai_api_key)

        # Agent Tools API: Grok runs web + X search server-side as needed.
        chat = client.chat.create(
            model=settings.grok_model,
            tools=[web_search(), x_search()],
        )
        chat.append(system(GROK_SYSTEM))
        chat.append(user(grok_user_prompt(niches, ecosystems, stages, target_count)))

        response = chat.sample()
    except Exception as exc:  # network / auth / quota
        raise RuntimeError(f"Grok search failed: {exc}") from exc

    notes = (getattr(response, "content", "") or "").strip()
    citations = list(getattr(response, "citations", []) or [])

    if not notes:
        raise RuntimeError("Grok returned no research notes. Try broadening your filters.")

    return SearchResult(notes=notes, citations=citations)
