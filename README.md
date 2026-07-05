# ⚡ Web3 LeadForge — BD Intelligence OS

A premium, dark-cyberpunk Streamlit app for the **Web3 Lead Generation Agent**.
Web research → AI scoring → ready-to-send outreach.

**Runs 100% free by default** — DuckDuckGo search + Google Gemini (free tier), no
paid credits. Flip two env vars to switch back to xAI Grok + Anthropic Claude
whenever you have credits.

![stack](https://img.shields.io/badge/Streamlit-wide-8b5cf6) ![free](https://img.shields.io/badge/Free-Gemini%20%2B%20DuckDuckGo-22c55e) ![grok](https://img.shields.io/badge/xAI-Grok-22d3ee) ![claude](https://img.shields.io/badge/Anthropic-Claude-6366f1)

## Providers — free vs paid
| Stage | Free (default) | Paid (switch to) |
|-------|----------------|------------------|
| **Search** | DuckDuckGo (no key) | Grok live web + X — `SEARCH_PROVIDER=grok` |
| **Scoring** | Gemini free tier — `ANALYZER_PROVIDER=gemini` | Claude — `=claude`, or Grok — `=grok` |

The free tier just needs a **free** Gemini key (no credit card):
<https://aistudio.google.com/apikey>

## Features
- **Run Search** — web search for high-intent founders/projects (DuckDuckGo free, or Grok live web+X).
- **Filters** — niches, ecosystems, stage, target count.
- **Scoring** — the AI dedupes and scores every lead **1–10** with reasoning.
- **Dashboard** — glassmorphism metric cards + Plotly charts (priority, niche, ecosystem).
- **Leads Table** — sortable, searchable, **priority color-coded** (green high → red low), CSV export.
- **Top 5** — expandable rich breakdowns of your hottest targets.
- **Outreach Studio** — a personalized **DM + Email** per lead, each with a one-click copy button.

## Project structure
```
app.py                 # main UI
requirements.txt
.env.example           # copy → .env, add your keys
src/
  config.py            # env + option catalogues + provider switches
  prompts.py           # system prompts + JSON schema
  styles.py            # all custom CSS (glassmorphism theme)
  search.py            # search dispatcher (free DuckDuckGo / Grok)
  free_search.py       # free DuckDuckGo research layer (no key)
  analyzer.py          # scoring + outreach — Gemini / Claude / Grok (forced JSON)
```

## Setup
```bash
# 1. Python 3.10+ required (install from python.org or: winget install Python.Python.3.12)
# 2. Create a virtual env (recommended)
python -m venv .venv && .venv\Scripts\activate     # Windows
# source .venv/bin/activate                         # macOS/Linux

# 3. Install deps
pip install -r requirements.txt

# 4. Configure — copy .env.example → .env, then add ONE free key:
copy .env.example .env        # then paste your free GEMINI_API_KEY
#   Get it (no credit card) at https://aistudio.google.com/apikey

# 5. Run
streamlit run app.py
```

### Switching back to xAI / Claude later
Edit `.env`:
```ini
SEARCH_PROVIDER=grok       # use Grok live web+X search (needs xAI credits)
ANALYZER_PROVIDER=claude   # or =grok — score with Claude/Grok instead of Gemini
```
Then restart the app. The sidebar shows the active mode (🟢 FREE / 💳 Paid).

## Model choice (batch lead scoring)
Set `ANALYZER_MODEL` in `.env`:

| Model | $/1M (in/out) | Use when |
|-------|---------------|----------|
| `claude-sonnet-4-6` *(default)* | $3 / $15 | **Recommended** — best cost/quality for batch scoring |
| `claude-opus-4-8` | $5 / $25 | Highest judgment quality |
| `claude-haiku-4-5` | $1 / $5 | Cheapest / fastest, lighter reasoning |

JSON output is forced via the Anthropic Messages API `output_config.format`
(json_schema) — responses are always valid, parseable JSON.

## 🔐 Security
- Keys live only in `.env`, which is **gitignored**. Never commit it.
- If you ever paste a key into chat, a screenshot, or a public repo, **rotate it**
  at the provider console immediately.
