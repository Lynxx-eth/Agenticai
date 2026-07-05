"""Web3 LeadForge — premium Streamlit app for the Web3 Lead Generation Agent.

Run:  streamlit run app.py
"""
from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analyzer import analyze
from src.config import ECOSYSTEMS, NICHES, STAGES, get_settings
from src.errors import render as render_alert
from src.mock import MOCK_CITATIONS, mock_dataframe
from src.search import run_search
from src.styles import inject_css

# ── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Web3 LeadForge | Growth Agency OS",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)
inject_css(st)

settings = get_settings()

_search_word = "DuckDuckGo" if settings.search_provider == "free" else "Grok"
_score_word = {"gemini": "Gemini", "claude": "Claude", "grok": "Grok"}.get(
    settings.analysis_provider or "", "AI"
)
HERO_SUB = f"{_search_word} research → {_score_word} scoring → ready-to-send outreach."

# Plotly theme constants
PLOT_BG = "rgba(0,0,0,0)"
GRID = "rgba(255,255,255,0.06)"
FONT = dict(family="Inter, sans-serif", color="#aab0c6", size=12)
VIOLET, CYAN, BLUE = "#8b5cf6", "#22d3ee", "#6366f1"


# ── Small helpers ────────────────────────────────────────────────────────────
def icon(path: str) -> str:
    return (
        f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


ICONS = {
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
}


def score_class(score: int) -> str:
    return "score-hi" if score >= 8 else "score-mid" if score >= 5 else "score-lo"


def metric_card(ico_key: str, value, label: str, trend: str = "") -> str:
    trend_html = f'<div class="lf-metric-trend">{html.escape(trend)}</div>' if trend else ""
    return (
        f'<div class="lf-metric"><div class="lf-metric-ico">{icon(ICONS[ico_key])}</div>'
        f'<div class="lf-metric-val">{value}</div>'
        f'<div class="lf-metric-lbl">{html.escape(label)}</div>{trend_html}</div>'
    )


def style_dataframe(df: pd.DataFrame):
    """Priority-color the score column (green high → red low) for st.dataframe."""
    def color_score(v):
        try:
            v = int(v)
        except (TypeError, ValueError):
            return ""
        if v >= 8:
            return "background-color: rgba(34,197,94,.18); color:#86efac; font-weight:600;"
        if v >= 5:
            return "background-color: rgba(245,158,11,.18); color:#fcd34d; font-weight:600;"
        return "background-color: rgba(239,68,68,.18); color:#fca5a5; font-weight:600;"

    return df.style.map(color_score, subset=["priority_score"])


# ── Charts ───────────────────────────────────────────────────────────────────
def chart_priority(df: pd.DataFrame) -> go.Figure:
    counts = df["priority_score"].value_counts().sort_index()
    colors = ["#ef4444" if s < 5 else "#f59e0b" if s < 8 else "#22c55e" for s in counts.index]
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values, marker_color=colors,
                           marker_line_width=0, hovertemplate="Score %{x}: %{y} leads<extra></extra>"))
    fig.update_layout(
        title="Priority Distribution", height=300, margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, font=FONT,
        xaxis=dict(title="Score", gridcolor=GRID, dtick=1),
        yaxis=dict(title="Leads", gridcolor=GRID),
        title_font=dict(family="Space Grotesk", size=15, color="#eef1f8"),
    )
    return fig


def chart_breakdown(df: pd.DataFrame, col: str, title: str) -> go.Figure:
    counts = df[col].replace("", "Unknown").value_counts().head(8).sort_values()
    fig = go.Figure(go.Bar(
        x=counts.values, y=counts.index, orientation="h",
        marker=dict(color=counts.values, colorscale=[[0, BLUE], [1, CYAN]], line_width=0),
        hovertemplate="%{y}: %{x}<extra></extra>",
    ))
    fig.update_layout(
        title=title, height=300, margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, font=FONT,
        xaxis=dict(gridcolor=GRID), yaxis=dict(gridcolor=GRID),
        title_font=dict(family="Space Grotesk", size=15, color="#eef1f8"),
    )
    return fig


def chart_ecosystem(df: pd.DataFrame) -> go.Figure:
    counts = df["ecosystem"].replace("", "Unknown").value_counts().head(7)
    palette = ["#8b5cf6", "#22d3ee", "#6366f1", "#a78bfa", "#3b82f6", "#67e8f9", "#c4b5fd"]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.62,
        marker=dict(colors=palette, line=dict(color="#0a0a14", width=2)),
        textinfo="percent", hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        title="Ecosystem Mix", height=300, margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, font=FONT,
        showlegend=True, legend=dict(font=dict(size=10)),
        title_font=dict(family="Space Grotesk", size=15, color="#eef1f8"),
    )
    return fig


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="lf-brand"><div class="lf-logo">⚡</div>'
        '<div><div class="lf-brand-name">LeadForge</div>'
        '<div class="lf-brand-sub">Web3 BD Intelligence</div></div></div>',
        unsafe_allow_html=True,
    )

    nav = st.radio("Navigate", ["Dashboard", "Leads Table", "Top 5", "Outreach"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="lf-section-title">Connections</div>', unsafe_allow_html=True)

    mode_badge = "🟢 FREE mode" if settings.is_free_mode else "💳 Paid mode"
    st.caption(mode_badge)
    search_label = "DuckDuckGo (free)" if settings.search_provider == "free" else f"Grok · {settings.grok_model}"
    st.caption(f"🔎 search · {search_label}")
    st.caption(f"🧠 scoring · {settings.scorer_label}")

    if settings.search_provider == "free" and settings.analysis_provider == "gemini" and not settings.gemini_ready:
        st.warning("Add a **free** GEMINI_API_KEY to `.env`, then restart.", icon="⚠️")
    elif settings.analysis_provider is None:
        st.warning("No scoring key set. Add GEMINI_API_KEY (free) to `.env`, then restart.", icon="⚠️")
    elif settings.is_free_mode:
        st.info("Running **100% free** — DuckDuckGo search + Gemini scoring. "
                "Set `SEARCH_PROVIDER=grok` in `.env` to switch to xAI later.", icon="✨")

    st.markdown("---")
    if st.button("✨  Load Demo Data", use_container_width=True):
        st.session_state["leads"] = mock_dataframe()
        st.session_state["citations"] = MOCK_CITATIONS
        st.toast("Loaded 8 sample leads — explore every tab.", icon="✨")
    st.caption("Preview the UI with sample leads (no keys / API calls).")


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="lf-hero"><div class="lf-hero-row">'
    '<div><div class="lf-title">LeadForge • Web3 BD Intelligence</div>'
    f'<div class="lf-sub">{html.escape(HERO_SUB)}</div></div>'
    '<div class="lf-pill"><span class="lf-dot"></span>Agency OS</div>'
    '</div></div>',
    unsafe_allow_html=True,
)


# ── Search controls (always visible) ─────────────────────────────────────────
with st.container():
    st.markdown('<div class="lf-section-title">Run Lead Search</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        sel_niches = st.multiselect("Niches", NICHES, default=["DeFi", "AI x Crypto", "Restaking"])
    with c2:
        sel_eco = st.multiselect("Ecosystems", ECOSYSTEMS, default=["Ethereum", "Base", "Solana"])
    with c3:
        sel_stage = st.multiselect("Stage", STAGES, default=["Seed", "Pre-token / Testnet"])

    c4, c5 = st.columns([1, 3])
    with c4:
        count = st.slider("Target leads", 5, 40, 15, step=5)
    with c5:
        st.write("")
        st.write("")
        run = st.button("🚀  Run Search", use_container_width=True, type="primary")

if run:
    if settings.analysis_provider is None:
        render_alert(st, "Gemini API key missing. Add GEMINI_API_KEY (free) to your .env.")
    else:
        search_label = "DuckDuckGo" if settings.search_provider == "free" else "Grok"
        scorer_label = _score_word
        run_error: str | None = None
        try:
            with st.status(f"Researching with {search_label}…", expanded=True) as status:
                st.write("🔎 Searching the web for high-intent signals…")
                result = run_search(settings, sel_niches, sel_eco, sel_stage, count)
                st.write(f"✅ Gathered notes ({len(result.citations)} sources).")
                st.write(f"🧠 Scoring & writing outreach with {scorer_label}…")
                df = analyze(settings, result.notes)
                st.write(f"✅ {len(df)} leads scored.")
                status.update(label=f"Done — {len(df)} leads ready", state="complete", expanded=False)
            st.session_state["leads"] = df
            st.session_state["citations"] = result.citations
        except RuntimeError as exc:
            run_error = str(exc)
        except Exception as exc:  # safety net — never show a raw traceback
            run_error = str(exc)

        if run_error:
            status.update(label="Run stopped", state="error", expanded=False)
            render_alert(st, run_error)
            st.caption("💡 Tip: click **✨ Load Demo Data** in the sidebar to explore the app with sample leads — free, no API calls.")


df: pd.DataFrame | None = st.session_state.get("leads")


def empty_state(msg: str = "No leads yet"):
    st.markdown(
        f'<div class="lf-empty"><div class="lf-empty-ico">🛰️</div>'
        f'<h3>{html.escape(msg)}</h3>'
        '<p>Pick your niches, ecosystems and stage above, then hit <b>Run Search</b>.</p></div>',
        unsafe_allow_html=True,
    )


# ── DASHBOARD ────────────────────────────────────────────────────────────────
if nav == "Dashboard":
    if df is None or df.empty:
        empty_state()
    else:
        total = len(df)
        avg = round(df["priority_score"].mean(), 1)
        hot = int((df["priority_score"] >= 8).sum())
        ecos = df["ecosystem"].replace("", pd.NA).dropna().nunique()
        st.markdown(
            '<div class="lf-grid">'
            + metric_card("users", total, "Total Leads")
            + metric_card("flame", hot, "Hot (8-10)", f"{round(hot / total * 100)}% of pipeline" if total else "")
            + metric_card("target", avg, "Avg Priority")
            + metric_card("globe", ecos, "Ecosystems")
            + "</div>",
            unsafe_allow_html=True,
        )
        a, b, c = st.columns(3)
        with a:
            st.plotly_chart(chart_priority(df), use_container_width=True, config={"displayModeBar": False})
        with b:
            st.plotly_chart(chart_breakdown(df, "niche", "Top Niches"), use_container_width=True, config={"displayModeBar": False})
        with c:
            st.plotly_chart(chart_ecosystem(df), use_container_width=True, config={"displayModeBar": False})


# ── LEADS TABLE ──────────────────────────────────────────────────────────────
elif nav == "Leads Table":
    if df is None or df.empty:
        empty_state()
    else:
        st.markdown('<div class="lf-section-title">All Leads</div>', unsafe_allow_html=True)
        f1, f2 = st.columns([3, 1])
        with f1:
            q = st.text_input("Search name / project / handle", placeholder="Filter…", label_visibility="collapsed")
        with f2:
            min_score = st.selectbox("Min score", [0, 5, 7, 8, 9], index=0)

        view = df.copy()
        if q:
            mask = view.apply(lambda r: q.lower() in " ".join(map(str, r.values)).lower(), axis=1)
            view = view[mask]
        view = view[view["priority_score"] >= min_score]

        st.dataframe(
            style_dataframe(view),
            use_container_width=True,
            height=560,
            column_config={
                "priority_score": st.column_config.NumberColumn("Priority", format="%d ⭐", width="small"),
                "handle": st.column_config.TextColumn("Handle", width="small"),
                "source_url": st.column_config.LinkColumn("Source", width="small"),
                "dm": st.column_config.TextColumn("DM", width="medium"),
                "email": st.column_config.TextColumn("Email", width="medium"),
            },
        )
        st.download_button(
            "⬇️  Export CSV",
            view.to_csv(index=False).encode("utf-8"),
            file_name="leadforge_leads.csv",
            mime="text/csv",
        )


# ── TOP 5 ────────────────────────────────────────────────────────────────────
elif nav == "Top 5":
    if df is None or df.empty:
        empty_state()
    else:
        st.markdown('<div class="lf-section-title">Top 5 — Priority Targets</div>', unsafe_allow_html=True)
        for i, (_, row) in enumerate(df.head(5).iterrows(), start=1):
            s = int(row["priority_score"])
            with st.expander(f"#{i}  ·  {row['name']}  —  {row['project']}   ⭐ {s}/10", expanded=(i == 1)):
                meta = "".join(
                    f'<span class="lf-chip">{html.escape(str(row[k]))}</span>'
                    for k in ("niche", "ecosystem", "stage") if str(row[k]).strip()
                )
                handle = html.escape(str(row["handle"]))
                st.markdown(
                    f'<div class="lf-lead-head"><div>'
                    f'<span class="lf-rank">RANK #{i}</span> '
                    f'<span class="lf-lead-name">{html.escape(str(row["name"]))}</span> '
                    f'<span class="lf-lead-handle">{handle}</span>'
                    f'<div class="lf-meta">{meta}</div></div>'
                    f'<div class="lf-score {score_class(s)}">{s}<small>SCORE</small></div></div>'
                    f'<div class="lf-signal"><b>Signal:</b> {html.escape(str(row["signal"]))}</div>'
                    f'<div class="lf-signal"><b>Why this score:</b> {html.escape(str(row["reasoning"]))}</div>',
                    unsafe_allow_html=True,
                )
                if str(row["source_url"]).strip():
                    st.markdown(f"🔗 [Source]({row['source_url']})")
                dm_col, em_col = st.columns(2)
                with dm_col:
                    st.caption("Direct message")
                    st.code(str(row["dm"]), language=None)
                with em_col:
                    st.caption("Email")
                    st.code(str(row["email"]), language=None)


# ── OUTREACH ─────────────────────────────────────────────────────────────────
elif nav == "Outreach":
    if df is None or df.empty:
        empty_state()
    else:
        st.markdown('<div class="lf-section-title">Outreach Studio</div>', unsafe_allow_html=True)
        st.caption("Every DM and email is personalized to the lead's live signal. Click the copy icon on any block.")
        for _, row in df.iterrows():
            s = int(row["priority_score"])
            with st.container():
                st.markdown(
                    f'<div class="lf-lead"><div class="lf-lead-head"><div>'
                    f'<span class="lf-lead-name">{html.escape(str(row["name"]))}</span> '
                    f'<span class="lf-lead-handle">{html.escape(str(row["handle"]))}</span>'
                    f'<div class="lf-meta">'
                    f'<span class="lf-chip">{html.escape(str(row["project"]))}</span>'
                    f'<span class="lf-chip">{html.escape(str(row["niche"]))}</span>'
                    f'<span class="lf-chip">{html.escape(str(row["ecosystem"]))}</span></div>'
                    f'<div class="lf-signal">{html.escape(str(row["signal"]))}</div></div>'
                    f'<div class="lf-score {score_class(s)}">{s}<small>SCORE</small></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
                t1, t2 = st.tabs(["💬 DM", "✉️ Email"])
                with t1:
                    st.code(str(row["dm"]), language=None)
                with t2:
                    st.code(str(row["email"]), language=None)
