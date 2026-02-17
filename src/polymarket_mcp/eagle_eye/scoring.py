"""Scoring primitives for impact/relevance ranking."""

from __future__ import annotations

import math
from datetime import datetime, timezone

from .models import SourceEvent

SOURCE_WEIGHT = {
    "polygon": 0.95,
    "polymarket": 0.9,
    "squawk": 0.8,
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _recency_score(timestamp: datetime, now: datetime) -> float:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    age_minutes = max((now - timestamp).total_seconds() / 60.0, 0.0)
    return math.exp(-age_minutes / 240.0)  # ~4h half-life


def compute_impact_score(event: SourceEvent) -> tuple[float, float]:
    """Compute impact + signed directional signal for an event."""
    probability_change = _safe_float(
        event.metadata.get("probability_change") or event.metadata.get("probability_change_24h")
    )
    change_pct = _safe_float(event.metadata.get("change_pct"))
    volume_24h = _safe_float(event.metadata.get("volume_24h"))
    liquidity = _safe_float(event.metadata.get("liquidity"))

    probability_signal = _clamp(abs(probability_change) / 0.2)  # 20 pts -> 1.0
    price_signal = _clamp(abs(change_pct) / 5.0)  # 5% move -> 1.0
    volume_signal = _clamp(math.log1p(max(volume_24h, 0.0)) / math.log1p(5_000_000.0))
    liquidity_signal = _clamp(math.log1p(max(liquidity, 0.0)) / math.log1p(5_000_000.0))
    hint_signal = _clamp(_safe_float(event.impact_hint))

    impact = (
        0.35 * probability_signal
        + 0.35 * price_signal
        + 0.2 * volume_signal
        + 0.1 * max(liquidity_signal, hint_signal)
    )

    directional_signal = probability_change if probability_change else change_pct / 100.0
    return _clamp(impact), directional_signal


def compute_relevance_score(event: SourceEvent, now: datetime | None = None) -> float:
    """Compute relevance from source reliability, confidence, and recency."""
    now = now or datetime.now(timezone.utc)
    source_base = SOURCE_WEIGHT.get(event.source.lower(), 0.7)
    confidence = _clamp(_safe_float(event.confidence, default=0.6))
    hint = _clamp(_safe_float(event.relevance_hint))
    recency = _recency_score(event.timestamp, now)

    relevance = (0.4 * source_base) + (0.3 * confidence) + (0.2 * recency) + (0.1 * hint)
    return _clamp(relevance)


def compute_event_score(event: SourceEvent, now: datetime | None = None) -> tuple[float, float, float, float]:
    """Return impact, relevance, total score, and directional signal."""
    now = now or datetime.now(timezone.utc)
    impact, directional_signal = compute_impact_score(event)
    relevance = compute_relevance_score(event, now=now)
    total = _clamp((0.6 * impact) + (0.4 * relevance))
    return impact, relevance, total, directional_signal

