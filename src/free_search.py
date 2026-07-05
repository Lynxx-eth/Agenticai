"""Free research layer — DuckDuckGo web search, no API key required.

Stands in for Grok's live search when the app runs in free mode. It fires a
handful of targeted queries built from the user's niche/ecosystem/stage filters,
collects the result snippets, and hands them to the analyzer as raw notes — the
same shape `src/search.py` returns, so the rest of the pipeline is unchanged.

Quality note: DuckDuckGo snippets are broader and less "live" than Grok's web+X
search, so the analyzer (Gemini) does more of the heavy lifting to pull real
leads out of the notes. It's free and needs zero keys.
"""
from __future__ import annotations

from .search import SearchResult


def _ddgs_text(query: str, max_results: int) -> list[dict]:
    """Run one DuckDuckGo text search, tolerant of both package names.

    `ddgs` is the maintained package; `duckduckgo_search` is the older import.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Free search needs the 'ddgs' package. Run: pip install -r requirements.txt"
            ) from exc
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as exc:  # network / DDG throttling
        raise RuntimeError(f"Free web search failed: {exc}") from exc


def _build_queries(
    niches: list[str],
    ecosystems: list[str],
    stages: list[str],
    target_count: int,
) -> list[str]:
    """Turn the filter selections into a small set of high-signal search queries."""
    niches = niches or ["web3"]
    ecosystems = ecosystems or [""]
    # Use the first word of each stage as a keyword (e.g. "Pre-token / Testnet" → "pre-token").
    stage_kw = " OR ".join(s.split()[0].lower() for s in stages) if stages else "seed"

    queries: list[str] = []
    for niche in niches:
        for eco in ecosystems:
            eco_s = f"{eco} " if eco else ""
            queries.append(
                f"new {niche} {eco_s}crypto project 2026 raised {stage_kw} funding founder"
            )
            queries.append(
                f"{niche} {eco_s}web3 startup launch OR hiring growth 2026 twitter"
            )
    # Cap so a run stays fast (~1s/query) while scaling a little with the target.
    cap = max(4, min(12, target_count))
    return queries[:cap]


def run_free_search(
    niches: list[str],
    ecosystems: list[str],
    stages: list[str],
    target_count: int,
) -> SearchResult:
    """Gather research notes via DuckDuckGo. Raises RuntimeError on failure."""
    queries = _build_queries(niches, ecosystems, stages, target_count)
    per_query = max(3, min(6, (target_count // len(queries)) + 3))

    blocks: list[str] = []
    citations: list[str] = []
    seen: set[str] = set()

    for query in queries:
        for hit in _ddgs_text(query, per_query):
            url = (hit.get("href") or hit.get("url") or "").strip()
            title = (hit.get("title") or "").strip()
            body = (hit.get("body") or "").strip()
            if not (title or body):
                continue
            key = url or title
            if key in seen:
                continue
            seen.add(key)
            blocks.append(f"- {title}\n  {body}\n  Source: {url}")
            if url:
                citations.append(url)

    if not blocks:
        raise RuntimeError(
            "Free search returned no results. Try broadening your niches/ecosystems, "
            "or DuckDuckGo may be rate-limiting — wait a minute and retry."
        )

    notes = (
        "Raw web search snippets gathered from DuckDuckGo. Each block is a real "
        "search result (title, summary, source URL). Extract genuine Web3 leads "
        "from these; ignore listicles, exchanges, and price pages.\n\n"
        + "\n".join(blocks)
    )
    return SearchResult(notes=notes, citations=citations[:30])
