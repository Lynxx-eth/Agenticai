"""Friendly, designed alerts.

Turns raw exceptions / SDK error strings into a clean glass alert card with an
icon, plain-English explanation, and a suggested next step. Keeps the technical
detail tucked away in a collapsible <details> for debugging.
"""
from __future__ import annotations

import html
from dataclasses import dataclass, field


@dataclass
class Alert:
    title: str
    message: str
    icon: str = "⚠️"
    severity: str = "err"  # err | warn | info
    actions: list[tuple[str, str]] = field(default_factory=list)  # (label, url)


# Ordered keyword rules — first match wins. Keep checks lowercase.
def classify(raw: str) -> Alert:
    t = (raw or "").lower()

    if any(k in t for k in ("gemini api key missing", "aistudio")):
        return Alert(
            icon="🔑",
            title="Free Gemini key not set",
            message=(
                "The app runs on Google Gemini's free tier for scoring. Grab a free key "
                "(no credit card) and add GEMINI_API_KEY to your .env, then restart."
            ),
            severity="warn",
            actions=[("Get a free Gemini key", "https://aistudio.google.com/apikey")],
        )

    if any(k in t for k in ("quota", "resource_exhausted", "exceeded your current quota")) and "gemini" in t:
        return Alert(
            icon="⏳",
            title="Gemini free-tier limit hit",
            message=(
                "You've reached Gemini's free requests-per-minute (or daily) limit. "
                "Wait a minute and retry, or lower the target-leads count."
            ),
            severity="warn",
        )

    if any(k in t for k in ("credit", "spending limit", "purchase more", "insufficient funds", "billing")):
        return Alert(
            icon="💳",
            title="xAI account is out of credits",
            message=(
                "Your Grok request was rejected because the team has used all its credits or "
                "hit its monthly spending limit. The app and your key are working — it just "
                "needs a balance to run live searches."
            ),
            actions=[("Add credits / raise limit", "https://console.x.ai")],
        )

    if any(k in t for k in ("rate limit", "429", "resource_exhausted", "too many requests")):
        return Alert(
            icon="⏳",
            title="Rate limited",
            message="You've sent requests too quickly. Wait a minute and try again, or lower the target-leads count.",
            severity="warn",
        )

    if any(k in t for k in ("unauthenticated", "invalid api key", "401", "authentication", "incorrect api key", "permission denied")):
        return Alert(
            icon="🔑",
            title="API key was rejected",
            message=(
                "The key in your .env was refused. Double-check it's correct and active, then "
                "restart the app so the new value loads."
            ),
            actions=[("Manage xAI keys", "https://console.x.ai"),
                     ("Manage Claude keys", "https://console.anthropic.com")],
        )

    if any(k in t for k in ("key missing", "malformed", "no analysis key", "no api key")):
        return Alert(
            icon="🗝️",
            title="API key not set",
            message="Add your key to the .env file (see .env.example), then restart the app.",
            severity="warn",
        )

    if any(k in t for k in ("unimplemented", "deprecated")):
        return Alert(
            icon="🛰️",
            title="xAI API endpoint changed",
            message="The xAI endpoint this used has moved. Update xai-sdk (pip install -U xai-sdk) or let me know.",
        )

    if any(k in t for k in ("connection", "timeout", "timed out", "network", "unavailable", "503", "getaddrinfo", "dns")):
        return Alert(
            icon="📡",
            title="Connection problem",
            message="Couldn't reach the API. Check your internet connection and try again.",
            severity="warn",
        )

    if any(k in t for k in ("not installed",)):
        return Alert(
            icon="📦",
            title="A package is missing",
            message="Install dependencies: pip install -r requirements.txt",
            severity="warn",
        )

    if any(k in t for k in ("parse", "json")):
        return Alert(
            icon="🧩",
            title="The model returned an unexpected format",
            message="The AI's response couldn't be read cleanly. This is usually transient — just run the search again.",
            severity="warn",
        )

    if any(k in t for k in ("no research notes", "no leads", "could not be extracted")):
        return Alert(
            icon="🔍",
            title="No leads found",
            message="The search came back empty. Try broadening your niches/ecosystems, or raising the target-leads count.",
            severity="info",
        )

    # Fallback — still friendly, with raw detail collapsed.
    return Alert(
        icon="⚠️",
        title="Something went wrong",
        message="The run didn't complete. The technical detail is below if you need it.",
    )


def render(st, raw: str) -> None:
    """Render a classified alert card for an error string."""
    a = classify(raw)
    actions = "".join(
        f'<a class="lf-alert-btn{"" if i == 0 else " ghost"}" href="{html.escape(url)}" target="_blank">{html.escape(label)} ↗</a>'
        for i, (label, url) in enumerate(a.actions)
    )
    actions_html = f'<div class="lf-alert-actions">{actions}</div>' if actions else ""
    detail_html = (
        f"<details><summary>Technical detail</summary><pre>{html.escape(raw)}</pre></details>"
    )
    st.markdown(
        f'<div class="lf-alert {a.severity}"><div class="lf-alert-ico">{a.icon}</div>'
        f'<div class="lf-alert-body"><p class="lf-alert-title">{html.escape(a.title)}</p>'
        f'<p class="lf-alert-msg">{html.escape(a.message)}</p>{actions_html}{detail_html}</div></div>',
        unsafe_allow_html=True,
    )
