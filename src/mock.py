"""Sample lead data for Demo Mode — lets you preview the full UI with no keys
or API calls. Entirely fictional; for design preview only.
"""
from __future__ import annotations

import pandas as pd

from .prompts import TABLE_COLUMNS

_SAMPLE: list[dict] = [
    {
        "name": "Maya Okonkwo", "handle": "@maya_builds", "project": "Velar Finance",
        "niche": "DEX / Perps", "ecosystem": "Base", "stage": "Seed",
        "priority_score": 9,
        "signal": "Closed a $4.2M seed last week and is publicly hiring a Head of Growth.",
        "reasoning": "Fresh raise + open growth role + active founder = textbook hot agency lead.",
        "dm": "Hey Maya — congrats on the seed 👏 Saw you're hiring for growth at Velar. We've taken 3 Base perps protocols from launch to 20k+ active traders. Worth a 15-min swap on your GTM plan?",
        "email": "Subject: Velar's growth hire — a shortcut\n\nHi Maya,\n\nCongrats on the $4.2M raise. Noticed you're hiring a Head of Growth — usually a 3-month search. We embed as a fractional growth team for Base-native perps protocols and have driven 20k+ active traders for similar launches. Could share a 1-page Velar GTM teardown if useful. Open to 15 minutes next week?\n\nBest,\nLeadForge",
        "source_url": "https://x.com/maya_builds",
    },
    {
        "name": "Devshad", "handle": "@0xdevshad", "project": "Reverb (restaking)",
        "niche": "Restaking", "ecosystem": "Ethereum", "stage": "Pre-token / Testnet",
        "priority_score": 8,
        "signal": "Testnet hit 50k wallets in 10 days; TGE rumored for next quarter.",
        "reasoning": "Strong traction with a token event ahead — peak window for growth + comms support.",
        "dm": "gm — Reverb's testnet numbers are wild (50k in 10 days). With a TGE on the horizon, the comms + KOL motion makes or breaks day one. We run exactly that for restaking protocols. Quick call?",
        "email": "Subject: Reverb TGE — the 30 days that matter\n\nHi Devshad,\n\n50k testnet wallets in 10 days is serious momentum. The window between now and TGE is where most restaking projects under-invest in comms and KOL coordination. We've run launch campaigns for two EigenLayer-adjacent protocols. Happy to share the playbook — 15 minutes?\n\nBest,\nLeadForge",
        "source_url": "https://x.com/0xdevshad",
    },
    {
        "name": "Lena Park", "handle": "@lenap_xyz", "project": "Synap AI",
        "niche": "AI x Crypto", "ecosystem": "Solana", "stage": "Pre-seed",
        "priority_score": 8,
        "signal": "Shipped an agent-marketplace demo that trended on CT this weekend.",
        "reasoning": "Viral moment + early stage means high need for narrative and BD help.",
        "dm": "Hey Lena — the Synap agent demo blew up on CT, deservedly. Early traction like that needs a narrative engine behind it before the hype fades. We do that for AI x crypto teams. Worth comparing notes?",
        "email": "Subject: Riding the Synap demo wave\n\nHi Lena,\n\nThe agent-marketplace demo trending this weekend was a great signal. The hard part is converting a viral moment into durable mindshare and partnerships before attention rotates. That's our wheelhouse for AI x crypto pre-seed teams. Could send a quick narrative audit — interested?\n\nBest,\nLeadForge",
        "source_url": "https://x.com/lenap_xyz",
    },
    {
        "name": "Tomi Adeyemi", "handle": "@tomi_onchain", "project": "Kindred Wallet",
        "niche": "Wallets", "ecosystem": "Solana", "stage": "Series A",
        "priority_score": 7,
        "signal": "Just announced a Series A; expanding into LatAm and hiring regionally.",
        "reasoning": "Funded and expanding, but later stage and may have in-house growth.",
        "dm": "Hey Tomi — saw the Series A + LatAm push 🌎 Regional growth is brutal without local KOL networks. We've got deep ones in BR/AR/MX. Could be a fast lever for Kindred. Quick chat?",
        "email": "Subject: Kindred's LatAm expansion — local levers\n\nHi Tomi,\n\nCongrats on the Series A. LatAm is a fantastic wallet market but notoriously hard to crack without on-the-ground KOL and community networks. We maintain those in Brazil, Argentina and Mexico. Could map a regional launch plan for Kindred in a short call — does next week work?\n\nBest,\nLeadForge",
        "source_url": "https://x.com/tomi_onchain",
    },
    {
        "name": "Iris Volkov", "handle": "@iris_zk", "project": "Penumbra Labs",
        "niche": "Privacy / ZK", "ecosystem": "Starknet", "stage": "Seed",
        "priority_score": 7,
        "signal": "Won a major ZK grant and shipped a mainnet alpha this month.",
        "reasoning": "Grant + mainnet alpha shows momentum; privacy niche needs careful messaging.",
        "dm": "Hi Iris — congrats on the grant and the mainnet alpha. Privacy projects live or die on how the narrative is framed. We've positioned two ZK protocols for mainstream traction without the FUD. Worth 15 min?",
        "email": "Subject: Framing Penumbra for mainstream ZK adoption\n\nHi Iris,\n\nThe grant win plus a mainnet alpha in one month is real momentum. Privacy/ZK is uniquely sensitive to narrative — the difference between 'compliance nightmare' and 'user sovereignty' is positioning. We've done that work for two ZK teams. Could share a messaging teardown — open to a quick call?\n\nBest,\nLeadForge",
        "source_url": "https://x.com/iris_zk",
    },
    {
        "name": "Raj Mehta", "handle": "@rajbuilds_eth", "project": "Flux RWA",
        "niche": "RWA (Real World Assets)", "ecosystem": "Ethereum", "stage": "Seed",
        "priority_score": 6,
        "signal": "Tokenizing private credit; announced a pilot with a fintech partner.",
        "reasoning": "Promising RWA angle but earlier in GTM; signal is a pilot, not live traction.",
        "dm": "Hey Raj — the Flux private-credit pilot is a smart wedge. RWA distribution is all about trust + the right institutional voices. We help RWA teams build exactly that credibility layer. Quick swap?",
        "email": "Subject: Flux RWA — building the credibility layer\n\nHi Raj,\n\nTokenizing private credit with a fintech pilot is a strong wedge. RWA adoption hinges on institutional trust and the right voices vouching for you. We've built that credibility motion for two RWA protocols. Happy to outline a distribution plan for Flux — got 15 minutes?\n\nBest,\nLeadForge",
        "source_url": "https://x.com/rajbuilds_eth",
    },
    {
        "name": "Nova DAO", "handle": "@novadao", "project": "Nova DAO",
        "niche": "DAOs", "ecosystem": "Arbitrum", "stage": "Token launched",
        "priority_score": 5,
        "signal": "Active treasury and a new grants program, but governance is slow-moving.",
        "reasoning": "Has budget via treasury, but DAO procurement cycles are long and uncertain.",
        "dm": "gm Nova — love the new grants program. Growth-as-a-service via a governance proposal could 10x your contributor funnel. We've shipped this with two DAOs. Want a draft proposal to react to?",
        "email": "Subject: A growth proposal for Nova DAO\n\nHi Nova team,\n\nThe new grants program is a great signal of intent. We partner with DAOs as a growth-as-a-service line item funded via governance — predictable scope, on-chain accountability. We've done this with two comparable DAOs. Could draft a proposal for the forum to react to. Worth exploring?\n\nBest,\nLeadForge",
        "source_url": "https://x.com/novadao",
    },
    {
        "name": "Kai Tanaka", "handle": "@kai_depin", "project": "GridLink",
        "niche": "DePIN", "ecosystem": "Solana", "stage": "Idea / Stealth",
        "priority_score": 4,
        "signal": "Stealth DePIN energy network; only a teaser site and waitlist so far.",
        "reasoning": "Compelling space but very early — no public traction or confirmed budget yet.",
        "dm": "Hey Kai — the GridLink teaser has me curious 👀 DePIN go-to-market is a different beast (hardware + supply + demand). We've helped two DePIN teams bootstrap both sides. Open to comparing notes early?",
        "email": "Subject: GridLink — DePIN GTM from day zero\n\nHi Kai,\n\nThe GridLink teaser is intriguing. DePIN is one of the hardest GTM problems — you're bootstrapping hardware supply and token demand simultaneously. We've helped two DePIN networks crack that chicken-and-egg. Happy to share what worked, even at the stealth stage. Quick call?\n\nBest,\nLeadForge",
        "source_url": "https://x.com/kai_depin",
    },
]


def mock_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(_SAMPLE)
    for col in TABLE_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[TABLE_COLUMNS]
    df = df.sort_values("priority_score", ascending=False).reset_index(drop=True)
    return df


MOCK_CITATIONS: list[str] = [
    "https://x.com/maya_builds", "https://x.com/0xdevshad",
    "https://x.com/lenap_xyz", "https://x.com/iris_zk",
]
