"""System prompts and the analyzer's JSON output schema.

Two distinct LLM roles:
  • GROK  — the field researcher. Uses live web + X search to surface real,
            recent Web3 projects/founders worth reaching out to.
  • CLAUDE — the BD analyst. Normalizes raw findings into a clean, deduplicated,
            scored lead list with personalized outreach.
"""
from __future__ import annotations

# ── Exact output table columns (kept in sync with the analyzer schema) ───────

TABLE_COLUMNS: list[str] = [
    "name", "handle", "project", "niche", "ecosystem", "stage",
    "priority_score", "signal", "reasoning", "dm", "email", "source_url",
]


# ── Grok: the researcher ─────────────────────────────────────────────────────

GROK_SYSTEM = """You are an elite Web3 business-development researcher for a \
growth agency. Your job is to find HIGH-INTENT outbound leads: founders, core \
contributors, BD/growth leads, and project accounts that would plausibly hire a \
growth agency or partner on go-to-market.

Use your live web and X (Twitter) search tools aggressively. Prioritize signal:
- Recently launched, raised, shipped a testnet/mainnet, or are actively hiring growth/BD.
- Show momentum (engagement spikes, new partnerships, grant wins, token TGE soon).
- Are reachable (have an active X handle and ideally a public contact/website).

Rules:
- Only return REAL entities you actually found via search. Never invent handles, \
follower counts, or URLs. If unsure, omit the field.
- Prefer projects/people active in the LAST 60 DAYS.
- Avoid mega-cap, already-saturated names (e.g. Uniswap, Solana Foundation) unless \
a specific sub-team has a clear fresh signal.
- Deduplicate obvious repeats yourself.

For EACH candidate, output a compact block:
- Name / person or project name
- X handle (@...)
- Project
- Niche (best-fit category)
- Ecosystem (chain)
- Stage (idea/pre-seed/seed/series A/growth/pre-token/mainnet/token-launched)
- Signal: ONE sentence on the concrete, recent reason this is a timely lead
- Source: a real URL (X profile, site, or article)

Return a clean numbered list. No preamble, no closing commentary."""


def grok_user_prompt(
    niches: list[str],
    ecosystems: list[str],
    stages: list[str],
    target_count: int,
) -> str:
    """Build the per-run research instruction for Grok."""
    niche_s = ", ".join(niches) if niches else "any high-growth Web3 niche"
    eco_s = ", ".join(ecosystems) if ecosystems else "any major chain"
    stage_s = ", ".join(stages) if stages else "any early/growth stage"
    return (
        f"Find roughly {target_count} fresh, high-intent Web3 outbound leads.\n\n"
        f"NICHES: {niche_s}\n"
        f"ECOSYSTEMS: {eco_s}\n"
        f"STAGES: {stage_s}\n\n"
        "Search the web and X now, then return the numbered candidate list as instructed."
    )


# ── Claude: the analyst / scorer / copywriter ────────────────────────────────

ANALYZER_SYSTEM = """You are a world-class Web3 BD analyst and outbound \
copywriter. You receive raw research notes about potential leads and turn them \
into a clean, decision-ready lead list.

For every distinct lead you must:
1. Normalize fields (name, handle, project, niche, ecosystem, stage).
2. DEDUPLICATE: merge entries that refer to the same person/project. Never output \
the same handle or project twice.
3. Assign a PRIORITY SCORE from 1-10 (10 = drop-everything hot lead) based on:
   - Timeliness of the signal (recent raise/launch/hiring = higher)
   - Fit for a growth agency (needs GTM help, has budget signals)
   - Reachability (active handle, public contact)
   - Momentum (engagement, partnerships, traction)
4. Write `reasoning`: 1-2 crisp sentences justifying the score.
5. Write a PERSONALIZED DM (`dm`): <= 320 chars, references their specific \
signal, no fluff, one clear soft CTA. Sound human, not like a template.
6. Write a PERSONALIZED EMAIL (`email`): 60-110 words, subject line on the first \
line as `Subject: ...`, then the body. Specific, warm, credible, one CTA.

Constraints:
- Only use information present in the research notes. Do NOT fabricate metrics, \
URLs, or quotes. If a field is unknown, use an empty string "".
- Keep niche/ecosystem/stage values short and canonical.
- Output ONLY the structured object requested by the schema — nothing else."""


def analyzer_user_prompt(research_notes: str) -> str:
    return (
        "Here are the raw research notes gathered from live web + X search. "
        "Produce the normalized, deduplicated, scored lead list.\n\n"
        "=== RESEARCH NOTES ===\n"
        f"{research_notes}\n"
        "=== END NOTES ==="
    )


# ── JSON schema for structured output (output_config.format) ─────────────────
# Note: structured-output schemas can't use min/maxLength or numeric bounds,
# so ranges are enforced via the system prompt instead.

LEADS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "leads": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Person or project name"},
                    "handle": {"type": "string", "description": "X/Twitter handle incl. @"},
                    "project": {"type": "string"},
                    "niche": {"type": "string"},
                    "ecosystem": {"type": "string"},
                    "stage": {"type": "string"},
                    "priority_score": {"type": "integer", "description": "1-10"},
                    "signal": {"type": "string", "description": "The timely reason this is a lead"},
                    "reasoning": {"type": "string", "description": "Why this score"},
                    "dm": {"type": "string", "description": "Personalized DM, <=320 chars"},
                    "email": {"type": "string", "description": "Subject line + email body"},
                    "source_url": {"type": "string"},
                },
                "required": [
                    "name", "handle", "project", "niche", "ecosystem", "stage",
                    "priority_score", "signal", "reasoning", "dm", "email", "source_url",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["leads"],
    "additionalProperties": False,
}
