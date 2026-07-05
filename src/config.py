"""Central configuration — reads secrets and options from the environment.

Keys are loaded from a local `.env` file (see `.env.example`) when running
locally, or from Streamlit **Secrets** when deployed to Streamlit Cloud (where
there is no `.env`). Nothing here is ever hardcoded; if a key is missing the UI
surfaces a friendly setup prompt rather than crashing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _load_streamlit_secrets() -> None:
    """Mirror Streamlit Cloud secrets into os.environ so `os.getenv` finds them.

    On Streamlit Cloud there is no `.env` file — keys live in `st.secrets`.
    Streamlit does not reliably expose those as environment variables, so we copy
    the top-level string secrets across here. Real env vars / `.env` values win
    (setdefault), and this is a silent no-op when Streamlit isn't running.
    """
    try:
        import streamlit as st

        for key, val in st.secrets.items():
            if isinstance(val, str):
                os.environ.setdefault(key, val)
    except Exception:
        # No streamlit, no secrets file, or malformed secrets — ignore and fall
        # back to environment / .env values.
        pass


_load_streamlit_secrets()


# ── Static option catalogues (used to build the filter controls) ─────────────

NICHES: list[str] = [
    "DeFi", "NFTs", "GameFi", "Infrastructure", "Layer 2 / Rollups",
    "RWA (Real World Assets)", "DePIN", "DAOs", "Stablecoins", "Wallets",
    "DEX / Perps", "Lending", "Restaking", "AI x Crypto", "SocialFi",
    "Privacy / ZK", "Bridges", "Oracles", "Launchpads", "Memecoins",
]

ECOSYSTEMS: list[str] = [
    "Ethereum", "Solana", "Base", "Arbitrum", "Optimism", "Polygon",
    "BNB Chain", "Avalanche", "Sui", "Aptos", "TON", "Bitcoin / Ordinals",
    "Cosmos", "Starknet", "zkSync", "Berachain", "Monad", "Hyperliquid",
]

STAGES: list[str] = [
    "Idea / Stealth", "Pre-seed", "Seed", "Series A", "Growth",
    "Pre-token / Testnet", "Mainnet live", "Token launched",
]


@dataclass(frozen=True)
class Settings:
    """Resolved runtime settings."""

    xai_api_key: str = field(default_factory=lambda: os.getenv("XAI_API_KEY", "").strip())
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "").strip())
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip())

    grok_model: str = field(default_factory=lambda: os.getenv("GROK_MODEL", "grok-4").strip())
    analyzer_model: str = field(default_factory=lambda: os.getenv("ANALYZER_MODEL", "claude-sonnet-4-6").strip())
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip())
    analyzer_effort: str = field(default_factory=lambda: os.getenv("ANALYZER_EFFORT", "low").strip().lower())

    # Provider switches. Defaults keep the app 100% free out of the box;
    # flip these (or add paid keys) to switch back to xAI Grok / Claude.
    #   SEARCH_PROVIDER   : free | grok
    #   ANALYZER_PROVIDER : gemini | claude | grok
    search_pref: str = field(default_factory=lambda: os.getenv("SEARCH_PROVIDER", "free").strip().lower())
    analyzer_pref: str = field(default_factory=lambda: os.getenv("ANALYZER_PROVIDER", "gemini").strip().lower())

    @property
    def grok_ready(self) -> bool:
        return self.xai_api_key.startswith("xai-")

    @property
    def claude_ready(self) -> bool:
        return self.anthropic_api_key.startswith("sk-ant-")

    @property
    def gemini_ready(self) -> bool:
        return len(self.gemini_api_key) > 10

    @property
    def supports_effort(self) -> bool:
        # Haiku tier does not accept the effort parameter.
        return not self.analyzer_model.startswith("claude-haiku")

    # ── Resolved providers ────────────────────────────────────────────────
    @property
    def search_provider(self) -> str:
        """Which engine finds the leads. 'free' (DuckDuckGo, no key) always
        works; opt into paid Grok by setting SEARCH_PROVIDER=grok."""
        if self.search_pref == "grok" and self.grok_ready:
            return "grok"
        return "free"

    @property
    def analysis_provider(self) -> str | None:
        """Which model scores the leads. An explicit ANALYZER_PROVIDER is always
        honored (a missing key then surfaces that provider's own 'add your key'
        message). Only 'auto'/unset falls back to the first key that's present."""
        pref = self.analyzer_pref
        if pref in ("gemini", "claude", "grok"):
            return pref
        if self.gemini_ready:
            return "gemini"
        if self.claude_ready:
            return "claude"
        if self.grok_ready:
            return "grok"
        return None

    @property
    def is_free_mode(self) -> bool:
        """True when the whole pipeline runs on free providers (no paid key used)."""
        return self.search_provider == "free" and self.analysis_provider == "gemini"

    @property
    def scorer_label(self) -> str:
        return {
            "gemini": self.gemini_model,
            "claude": self.analyzer_model,
            "grok": f"{self.grok_model} (Grok-only)",
        }.get(self.analysis_provider or "", "not configured")


def get_settings() -> Settings:
    """Build a fresh Settings snapshot (re-reads env each call)."""
    return Settings()
