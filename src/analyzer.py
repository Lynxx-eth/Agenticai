"""Claude analysis layer.

Takes Grok's raw research notes and returns a normalized, deduplicated,
priority-scored lead list with personalized outreach — using the Anthropic
Messages API with a forced JSON schema (output_config.format), so the result is
always valid, parseable JSON. No assistant prefills (they 400 on these models).
"""
from __future__ import annotations

import json
import re

import pandas as pd

from .config import Settings
from .prompts import (
    ANALYZER_SYSTEM,
    LEADS_SCHEMA,
    TABLE_COLUMNS,
    analyzer_user_prompt,
)


def _to_dataframe(leads: list[dict]) -> pd.DataFrame:
    """Normalize a raw list of lead dicts into the canonical, sorted DataFrame."""
    if not leads:
        raise RuntimeError("No leads could be extracted from the research notes.")
    df = pd.DataFrame(leads)
    for col in TABLE_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[TABLE_COLUMNS]
    df["priority_score"] = (
        pd.to_numeric(df["priority_score"], errors="coerce").fillna(0).clip(0, 10).astype(int)
    )
    return df.sort_values("priority_score", ascending=False).reset_index(drop=True)


def _extract_json(text: str) -> dict:
    """Tolerantly pull a JSON object out of a model response (strips code
    fences and any prose around it)."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def analyze(settings: Settings, research_notes: str) -> pd.DataFrame:
    """Score leads with whichever provider is configured — Gemini (free) by
    default, or Claude / Grok when selected via ANALYZER_PROVIDER."""
    provider = settings.analysis_provider
    if provider == "gemini":
        return analyze_with_gemini(settings, research_notes)
    if provider == "claude":
        return analyze_leads(settings, research_notes)
    if provider == "grok":
        return analyze_with_grok(settings, research_notes)
    raise RuntimeError(
        "No analysis key configured. Add GEMINI_API_KEY (free) — or ANTHROPIC_API_KEY / "
        "XAI_API_KEY — to your .env."
    )


def analyze_leads(settings: Settings, research_notes: str) -> pd.DataFrame:
    """Normalize + score the research notes into a tidy DataFrame.

    Raises RuntimeError with a readable message on failure.
    """
    if not settings.claude_ready:
        raise RuntimeError("Anthropic API key missing or malformed. Add ANTHROPIC_API_KEY to your .env.")

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("anthropic not installed. Run: pip install -r requirements.txt") from exc

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # output_config carries both the JSON-schema format and (optionally) effort.
    output_config: dict = {"format": {"type": "json_schema", "schema": LEADS_SCHEMA}}
    if settings.supports_effort and settings.analyzer_effort in {"low", "medium", "high"}:
        output_config["effort"] = settings.analyzer_effort

    try:
        response = client.messages.create(
            model=settings.analyzer_model,
            max_tokens=16000,
            system=ANALYZER_SYSTEM,
            output_config=output_config,
            messages=[{"role": "user", "content": analyzer_user_prompt(research_notes)}],
        )
    except anthropic.APIStatusError as exc:
        raise RuntimeError(f"Claude API error ({exc.status_code}): {exc.message}") from exc
    except Exception as exc:
        raise RuntimeError(f"Claude analysis failed: {exc}") from exc

    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined this request. Adjust the inputs and retry.")

    # With output_config.format the first text block is guaranteed valid JSON.
    text = next((b.text for b in response.content if b.type == "text"), "")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Could not parse Claude's JSON response.") from exc

    return _to_dataframe(data.get("leads", []))


def _json_instruction(research_notes: str) -> str:
    """Shared user prompt for providers without native schema-forcing (Grok, Gemini):
    asks for strict JSON of the exact lead shape."""
    schema_hint = json.dumps(LEADS_SCHEMA, indent=2)
    return (
        f"{analyzer_user_prompt(research_notes)}\n\n"
        "Return ONLY a JSON object of this exact shape (no markdown, no prose):\n"
        '{ "leads": [ { '
        '"name","handle","project","niche","ecosystem","stage",'
        '"priority_score" (integer 1-10),"signal","reasoning","dm","email","source_url" '
        "} ] }\n\n"
        f"JSON schema for reference:\n{schema_hint}"
    )


def analyze_with_gemini(settings: Settings, research_notes: str) -> pd.DataFrame:
    """Score + write outreach using Google Gemini — the free-tier default.

    Uses the google-genai SDK with JSON response mode. Requires a free API key
    from https://aistudio.google.com/apikey (no credit card).
    """
    if not settings.gemini_ready:
        raise RuntimeError(
            "Gemini API key missing. Get a free one at https://aistudio.google.com/apikey "
            "and add GEMINI_API_KEY to your .env."
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "google-genai not installed. Run: pip install -r requirements.txt"
        ) from exc

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=_json_instruction(research_notes),
            config=types.GenerateContentConfig(
                system_instruction=ANALYZER_SYSTEM,
                response_mime_type="application/json",
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )
    except Exception as exc:  # network / auth / quota
        raise RuntimeError(f"Gemini analysis failed: {exc}") from exc

    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response. Try again or broaden your filters.")
    try:
        data = _extract_json(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Could not parse Gemini's JSON response.") from exc

    return _to_dataframe(data.get("leads", []))


def analyze_with_grok(settings: Settings, research_notes: str) -> pd.DataFrame:
    """Score + write outreach using Grok only — no Claude key required.

    Grok is asked to return strict JSON matching the lead schema; the response
    is parsed tolerantly. Live search is OFF here (we already have the notes).
    """
    if not settings.grok_ready:
        raise RuntimeError("xAI API key missing or malformed. Add XAI_API_KEY to your .env.")

    try:
        from xai_sdk import Client
        from xai_sdk.chat import system, user
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("xai-sdk not installed. Run: pip install -r requirements.txt") from exc

    instruction = _json_instruction(research_notes)

    try:
        client = Client(api_key=settings.xai_api_key)
        chat = client.chat.create(model=settings.grok_model)  # no live search
        chat.append(system(ANALYZER_SYSTEM))
        chat.append(user(instruction))
        response = chat.sample()
    except Exception as exc:
        raise RuntimeError(f"Grok analysis failed: {exc}") from exc

    text = (getattr(response, "content", "") or "").strip()
    try:
        data = _extract_json(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Could not parse Grok's JSON response.") from exc

    return _to_dataframe(data.get("leads", []))
