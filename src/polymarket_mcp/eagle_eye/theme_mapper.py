"""Theme inference utilities for Eagle Eye narratives."""

from __future__ import annotations

from .models import SourceEvent

THEME_KEYWORDS: dict[str, set[str]] = {
    "Rates & Fed": {"fed", "fomc", "interest rate", "cpi", "inflation", "yield", "treasury"},
    "US Politics": {"election", "trump", "biden", "congress", "senate", "white house"},
    "Crypto Beta": {"btc", "bitcoin", "eth", "ethereum", "solana", "crypto", "defi"},
    "AI & Semis": {"ai", "openai", "nvidia", "semiconductor", "gpu", "datacenter"},
    "Energy & Commodities": {"oil", "wti", "brent", "gas", "gold", "commodity"},
    "Geopolitics": {"war", "nato", "sanction", "tariff", "china", "russia", "middle east"},
    "Sports & Entertainment": {"nfl", "nba", "soccer", "mlb", "oscar", "grammy"},
}


def infer_themes(event: SourceEvent) -> list[str]:
    """Infer one or more themes from normalized event text/tags."""
    text_parts = [event.title, event.summary or "", event.asset or ""]
    text_parts.extend(event.tags)
    text = " ".join(text_parts).lower()

    hits: list[str] = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            hits.append(theme)

    if hits:
        return hits
    if event.asset:
        return [f"Single Name: {event.asset.upper()}"]
    return ["Macro / Other"]

