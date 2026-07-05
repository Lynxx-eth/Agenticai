"""All custom CSS for Web3 LeadForge.

Dark cyberpunk / fintech aesthetic: deep-navy glass surfaces, electric
purple→cyan accents, JetBrains Mono tabular figures, subtle hover lifts.
Designed against WCAG-safe contrast on dark (primary text >= 4.5:1).

Call `inject_css(st)` once, right after `st.set_page_config(...)`.
"""
from __future__ import annotations

# Design tokens kept as CSS custom properties so the whole theme is tunable
# from one place.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg-0: #06060c;
  --bg-1: #0a0a14;
  --bg-2: #0f0f1c;
  --glass: rgba(22, 22, 40, 0.55);
  --glass-strong: rgba(28, 28, 50, 0.72);
  --border: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.14);
  --text-0: #eef1f8;
  --text-1: #aab0c6;
  --text-2: #717892;
  --violet: #8b5cf6;
  --violet-2: #a78bfa;
  --cyan: #22d3ee;
  --blue: #3b82f6;
  --grad: linear-gradient(120deg, #8b5cf6 0%, #6366f1 45%, #22d3ee 100%);
  --grad-soft: linear-gradient(120deg, rgba(139,92,246,.18), rgba(34,211,238,.12));
  --good: #22c55e;
  --warn: #f59e0b;
  --bad: #ef4444;
  --radius: 18px;
  --shadow: 0 10px 40px -12px rgba(0,0,0,.65);
  --shadow-glow: 0 0 0 1px rgba(139,92,246,.25), 0 12px 50px -10px rgba(99,102,241,.45);
}

/* ── Base canvas ─────────────────────────────────────────── */
.stApp {
  background:
    radial-gradient(1200px 600px at 12% -8%, rgba(99,102,241,.18), transparent 55%),
    radial-gradient(1000px 600px at 100% 0%, rgba(34,211,238,.12), transparent 50%),
    radial-gradient(900px 700px at 50% 120%, rgba(139,92,246,.14), transparent 55%),
    var(--bg-0);
  color: var(--text-0);
  font-family: 'Inter', -apple-system, system-ui, sans-serif;
}

/* Hide default Streamlit chrome for a cleaner app feel — but KEEP the header
   bar transparent so the sidebar collapse/expand toggle stays clickable. */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { visibility: visible !important; display: flex !important; }
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button { color: var(--text-0) !important; }
.block-container { padding-top: 1.4rem; padding-bottom: 4rem; max-width: 1500px; }

h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -.01em; color: var(--text-0); }
p, span, label, div { color: var(--text-0); }

/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(15,15,28,.92), rgba(8,8,16,.92));
  border-right: 1px solid var(--border);
  backdrop-filter: blur(18px);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }

.lf-brand {
  display:flex; align-items:center; gap:.7rem; margin: .2rem 0 1.4rem 0;
}
.lf-logo {
  width:38px; height:38px; border-radius:11px; background: var(--grad);
  display:flex; align-items:center; justify-content:center;
  box-shadow: 0 6px 22px -6px rgba(139,92,246,.7);
  font-weight:700; font-family:'Space Grotesk'; color:white; font-size:18px;
}
.lf-brand-name { font-family:'Space Grotesk'; font-weight:700; font-size:1.15rem; line-height:1; }
.lf-brand-sub { color: var(--text-2); font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; }

/* ── Hero header ─────────────────────────────────────────── */
.lf-hero {
  position:relative; border-radius: var(--radius); padding: 1.5rem 1.8rem;
  background: var(--glass); border:1px solid var(--border);
  backdrop-filter: blur(22px); box-shadow: var(--shadow);
  overflow:hidden; margin-bottom: 1.4rem;
}
.lf-hero::before {
  content:""; position:absolute; inset:0;
  background: var(--grad-soft); opacity:.7; pointer-events:none;
}
.lf-hero-row { position:relative; display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.lf-title {
  font-family:'Space Grotesk'; font-weight:700; font-size:1.9rem; line-height:1.1; margin:0;
  background: linear-gradient(90deg, #fff, #c7d2fe 55%, #67e8f9);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
}
.lf-sub { color: var(--text-1); font-size:.95rem; margin-top:.35rem; }
.lf-pill {
  display:inline-flex; align-items:center; gap:.45rem; padding:.42rem .8rem;
  border-radius:999px; font-size:.78rem; font-weight:600;
  background: rgba(34,211,238,.10); border:1px solid rgba(34,211,238,.30); color:#a5f3fc;
}
.lf-dot { width:8px; height:8px; border-radius:50%; background: var(--cyan); box-shadow:0 0 10px var(--cyan); animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

/* ── Glass cards / metrics ──────────────────────────────── */
.lf-grid { display:grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: .2rem 0 1.4rem; }
@media (max-width: 1100px){ .lf-grid { grid-template-columns: repeat(2,1fr);} }

.lf-metric {
  position:relative; border-radius: var(--radius); padding: 1.15rem 1.25rem;
  background: var(--glass); border:1px solid var(--border);
  backdrop-filter: blur(20px); box-shadow: var(--shadow);
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}
.lf-metric:hover { transform: translateY(-4px); box-shadow: var(--shadow-glow); border-color: var(--border-strong); }
.lf-metric-ico {
  width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;
  background: var(--grad-soft); border:1px solid var(--border-strong); margin-bottom:.7rem;
}
.lf-metric-ico svg { width:20px; height:20px; stroke:var(--violet-2); }
.lf-metric-val { font-family:'JetBrains Mono'; font-weight:600; font-size:1.9rem; line-height:1; font-variant-numeric: tabular-nums; }
.lf-metric-lbl { color: var(--text-2); font-size:.74rem; letter-spacing:.1em; text-transform:uppercase; margin-top:.45rem; }
.lf-metric-trend { font-size:.75rem; margin-top:.3rem; color: var(--good); font-weight:600; }

/* generic glass panel */
.lf-panel {
  border-radius: var(--radius); padding: 1.3rem 1.4rem;
  background: var(--glass); border:1px solid var(--border);
  backdrop-filter: blur(20px); box-shadow: var(--shadow); margin-bottom:1.1rem;
}
.lf-panel h3 { margin:.1rem 0 1rem; font-size:1.05rem; }
.lf-section-title { font-family:'Space Grotesk'; font-weight:600; font-size:1.15rem; margin: .4rem 0 .9rem; display:flex; align-items:center; gap:.5rem; }
.lf-section-title::before { content:""; width:4px; height:20px; border-radius:4px; background: var(--grad); display:inline-block; }

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {
  border-radius: 12px; font-weight:600; font-family:'Inter'; border:1px solid var(--border-strong);
  background: var(--grad); color:white; padding:.6rem 1.1rem;
  transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
  box-shadow: 0 8px 26px -10px rgba(99,102,241,.8);
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-2px); filter: brightness(1.08);
  box-shadow: 0 12px 34px -8px rgba(99,102,241,.95);
}
.stButton > button:active { transform: translateY(0); }

/* ── Inputs / multiselect ────────────────────────────────── */
div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
  background: rgba(12,12,24,.7) !important; border:1px solid var(--border) !important;
  border-radius: 12px !important; color: var(--text-0) !important;
}
div[data-baseweb="select"] > div:hover { border-color: var(--violet) !important; }
span[data-baseweb="tag"] {
  background: var(--grad-soft) !important; border:1px solid rgba(139,92,246,.4) !important;
  color:#ddd6fe !important; border-radius:8px !important;
}
label, .stMultiSelect label, .stSlider label { color: var(--text-1) !important; font-weight:500; }

/* Dropdown popovers (multiselect + selectbox menus) — force dark so the
   option text is readable. These render in a portal at the page root. */
div[data-baseweb="popover"] [data-baseweb="menu"],
ul[role="listbox"], div[data-baseweb="menu"] {
  background: #10101e !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow) !important;
}
li[role="option"], div[data-baseweb="menu"] li, ul[role="listbox"] li {
  background: transparent !important;
  color: var(--text-0) !important;
}
li[role="option"]:hover, ul[role="listbox"] li:hover,
li[role="option"][aria-selected="true"] {
  background: var(--grad-soft) !important;
  color: #ffffff !important;
}
/* the text input row inside an open multiselect popover */
div[data-baseweb="popover"] input { color: var(--text-0) !important; }

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap:.4rem; border-bottom:1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
  background: transparent; color: var(--text-2); border-radius:10px 10px 0 0;
  padding:.5rem 1rem; font-weight:600; font-family:'Space Grotesk';
}
.stTabs [aria-selected="true"] {
  color: var(--text-0) !important; background: var(--glass);
  border:1px solid var(--border); border-bottom:2px solid var(--violet);
}

/* ── DataFrame ───────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border-radius: var(--radius); overflow:hidden; border:1px solid var(--border);
  box-shadow: var(--shadow); background: var(--glass-strong);
}
[data-testid="stDataFrame"] * { font-family:'Inter'; }

/* ── Lead / outreach cards ──────────────────────────────── */
.lf-lead {
  border-radius: var(--radius); padding:1.2rem 1.35rem; margin-bottom:1rem;
  background: var(--glass); border:1px solid var(--border); backdrop-filter: blur(18px);
  box-shadow: var(--shadow); transition: transform .2s ease, border-color .2s ease;
}
.lf-lead:hover { transform: translateY(-3px); border-color: var(--border-strong); }
.lf-lead-head { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap; }
.lf-lead-name { font-family:'Space Grotesk'; font-weight:700; font-size:1.15rem; }
.lf-lead-handle { color: var(--cyan); font-size:.85rem; font-family:'JetBrains Mono'; }
.lf-meta { display:flex; gap:.4rem; flex-wrap:wrap; margin:.6rem 0 .5rem; }
.lf-chip {
  font-size:.72rem; padding:.28rem .6rem; border-radius:999px;
  background: rgba(255,255,255,.05); border:1px solid var(--border); color: var(--text-1);
}
.lf-signal { color: var(--text-1); font-size:.9rem; line-height:1.5; margin-top:.3rem; }

.lf-score {
  font-family:'JetBrains Mono'; font-weight:600; font-size:1.6rem; font-variant-numeric: tabular-nums;
  min-width:64px; text-align:center; border-radius:14px; padding:.5rem .2rem; line-height:1;
  border:1px solid var(--border-strong);
}
.lf-score small { display:block; font-size:.55rem; letter-spacing:.12em; color: var(--text-2); margin-top:.3rem; font-family:'Inter'; }
.score-hi { background: rgba(34,197,94,.14); color:#86efac; border-color: rgba(34,197,94,.4); }
.score-mid{ background: rgba(245,158,11,.14); color:#fcd34d; border-color: rgba(245,158,11,.4); }
.score-lo { background: rgba(239,68,68,.14); color:#fca5a5; border-color: rgba(239,68,68,.4); }

.lf-rank {
  font-family:'JetBrains Mono'; font-weight:600; font-size:.8rem; color: var(--violet-2);
  background: var(--grad-soft); border:1px solid rgba(139,92,246,.35);
  border-radius:8px; padding:.2rem .5rem;
}

/* ── Expander ────────────────────────────────────────────── */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
  background: var(--glass) !important; border:1px solid var(--border) !important;
  border-radius: 12px !important; font-family:'Space Grotesk'; font-weight:600;
}
[data-testid="stExpander"] { border:none !important; }

/* ── Code blocks (copy buttons live here) ───────────────── */
[data-testid="stCode"], pre {
  background: rgba(8,8,16,.85) !important; border:1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stCode"] code { color:#dbeafe !important; }

/* ── Alerts / friendly errors ───────────────────────────── */
.lf-alert {
  display:flex; gap:1rem; align-items:flex-start;
  border-radius:16px; padding:1.15rem 1.3rem; margin:.4rem 0 1.1rem;
  background: var(--glass); border:1px solid var(--border);
  backdrop-filter: blur(18px); box-shadow: var(--shadow);
  border-left-width:4px;
}
.lf-alert.err  { border-left-color: var(--bad);  background: linear-gradient(90deg, rgba(239,68,68,.10), var(--glass)); }
.lf-alert.warn { border-left-color: var(--warn); background: linear-gradient(90deg, rgba(245,158,11,.10), var(--glass)); }
.lf-alert.info { border-left-color: var(--cyan); background: linear-gradient(90deg, rgba(34,211,238,.10), var(--glass)); }
.lf-alert-ico { font-size:1.5rem; line-height:1; margin-top:.1rem; flex-shrink:0; }
.lf-alert-body { flex:1; }
.lf-alert-title { font-family:'Space Grotesk'; font-weight:700; font-size:1.05rem; margin:0 0 .25rem; }
.lf-alert-msg { color: var(--text-1); font-size:.92rem; line-height:1.55; margin:0; }
.lf-alert-actions { margin-top:.7rem; display:flex; gap:.6rem; flex-wrap:wrap; }
.lf-alert-btn {
  display:inline-flex; align-items:center; gap:.4rem; text-decoration:none;
  font-size:.82rem; font-weight:600; padding:.45rem .85rem; border-radius:10px;
  background: var(--grad); color:#fff !important; border:1px solid var(--border-strong);
  transition: filter .15s ease, transform .15s ease;
}
.lf-alert-btn:hover { filter:brightness(1.1); transform:translateY(-1px); }
.lf-alert-btn.ghost { background: rgba(255,255,255,.05); color: var(--text-0) !important; }
.lf-alert details { margin-top:.7rem; }
.lf-alert summary { color: var(--text-2); font-size:.78rem; cursor:pointer; }
.lf-alert pre { color: var(--text-2); font-size:.72rem; white-space:pre-wrap; word-break:break-word; margin-top:.4rem; }

/* ── Empty state ─────────────────────────────────────────── */
.lf-empty {
  text-align:center; padding: 3.5rem 1rem; border-radius: var(--radius);
  background: var(--glass); border:1px dashed var(--border-strong);
}
.lf-empty-ico { font-size:2.4rem; margin-bottom:.6rem; }
.lf-empty h3 { color: var(--text-0); }
.lf-empty p { color: var(--text-2); }

/* scrollbar */
::-webkit-scrollbar { width:10px; height:10px; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,.35); border-radius:10px; }
::-webkit-scrollbar-track { background: transparent; }
</style>
"""


def inject_css(st) -> None:
    """Inject the full stylesheet. Call once after set_page_config."""
    st.markdown(CSS, unsafe_allow_html=True)
