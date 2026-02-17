"""Typed models for Eagle Eye event aggregation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceEvent(BaseModel):
    """Normalized event produced by a source adapter."""

    event_id: str
    source: str
    timestamp: datetime
    title: str
    summary: str | None = None
    asset: str | None = None
    tags: list[str] = Field(default_factory=list)
    impact_hint: float | None = None
    relevance_hint: float | None = None
    confidence: float = 0.6
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScoredEvent(SourceEvent):
    """SourceEvent enriched with scoring outputs."""

    themes: list[str] = Field(default_factory=list)
    impact_score: float
    relevance_score: float
    event_score: float
    directional_signal: float = 0.0


class Narrative(BaseModel):
    """Aggregated market narrative."""

    theme: str
    narrative_score: float
    impact_score: float
    relevance_score: float
    confidence: float
    trend: str
    event_count: int
    sources: list[str] = Field(default_factory=list)
    top_assets: list[str] = Field(default_factory=list)
    catalysts: list[str] = Field(default_factory=list)
    latest_event_at: datetime


class SourceHealth(BaseModel):
    """Operational state for each source adapter."""

    source: str
    status: str
    events: int = 0
    latency_ms: int | None = None
    error: str | None = None


class EagleEyeSnapshot(BaseModel):
    """Top-level response for dashboard views."""

    generated_at: datetime
    window_minutes: int
    events_analyzed: int
    narratives: list[Narrative] = Field(default_factory=list)
    source_health: list[SourceHealth] = Field(default_factory=list)

