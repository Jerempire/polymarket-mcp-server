"""Core Eagle Eye orchestration and aggregation logic."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from statistics import mean

from ..config import PolymarketConfig
from .adapters import PolygonAdapter, PolymarketAdapter, SourceAdapter, SquawkAdapter
from .models import EagleEyeSnapshot, Narrative, ScoredEvent, SourceEvent, SourceHealth
from .scoring import compute_event_score
from .theme_mapper import infer_themes

logger = logging.getLogger(__name__)


class EagleEyeService:
    """Aggregates market events into ranked narratives."""

    def __init__(self, config: PolymarketConfig):
        self.config = config
        self.adapters: list[SourceAdapter] = []
        self._cache_lock = asyncio.Lock()
        self._events_cache_at: datetime | None = None
        self._events_cache_key: tuple[int, int] | None = None
        self._events_cache: tuple[list[ScoredEvent], list[SourceHealth]] | None = None

        if self.config.EAGLE_EYE_ENABLE_POLYMARKET:
            self.adapters.append(PolymarketAdapter(config))
        if self.config.EAGLE_EYE_ENABLE_POLYGON:
            self.adapters.append(PolygonAdapter(config))
        if self.config.EAGLE_EYE_ENABLE_SQUAWK:
            self.adapters.append(SquawkAdapter(config))

    async def _pull_source(
        self,
        adapter: SourceAdapter,
        source_limit: int,
        now: datetime,
        window_minutes: int,
    ) -> tuple[list[SourceEvent], SourceHealth]:
        started = time.perf_counter()
        cutoff = now - timedelta(minutes=window_minutes)

        try:
            events = await adapter.fetch_events(source_limit)
            in_window: list[SourceEvent] = []
            for event in events:
                ts = event.timestamp if event.timestamp.tzinfo else event.timestamp.replace(tzinfo=timezone.utc)
                if ts >= cutoff:
                    in_window.append(event)

            latency_ms = int((time.perf_counter() - started) * 1000)
            status = "ok" if in_window else "degraded"
            return in_window, SourceHealth(
                source=adapter.source_name,
                status=status,
                events=len(in_window),
                latency_ms=latency_ms,
            )
        except Exception as exc:  # pragma: no cover - network failure path
            latency_ms = int((time.perf_counter() - started) * 1000)
            logger.warning("Source %s failed: %s", adapter.source_name, exc)
            return [], SourceHealth(
                source=adapter.source_name,
                status="error",
                events=0,
                latency_ms=latency_ms,
                error=str(exc),
            )

    async def _collect_scored_events(
        self,
        window_minutes: int,
        source_limit: int,
        use_cache: bool = True,
    ) -> tuple[list[ScoredEvent], list[SourceHealth]]:
        cache_key = (window_minutes, source_limit)
        now = datetime.now(timezone.utc)
        ttl_seconds = self.config.EAGLE_EYE_CACHE_TTL_SECONDS

        if use_cache:
            async with self._cache_lock:
                if (
                    self._events_cache
                    and self._events_cache_at
                    and self._events_cache_key == cache_key
                    and (now - self._events_cache_at).total_seconds() <= ttl_seconds
                ):
                    cached_events, cached_health = self._events_cache
                    return (
                        [event.model_copy(deep=True) for event in cached_events],
                        [health.model_copy(deep=True) for health in cached_health],
                    )

        now = datetime.now(timezone.utc)
        tasks = [
            self._pull_source(adapter, source_limit=source_limit, now=now, window_minutes=window_minutes)
            for adapter in self.adapters
        ]

        if not tasks:
            return [], []

        results = await asyncio.gather(*tasks)
        source_health = [health for _, health in results]
        source_events = [event for events, _ in results for event in events]

        scored_events: list[ScoredEvent] = []
        for event in source_events:
            themes = infer_themes(event)
            impact, relevance, total, directional = compute_event_score(event, now=now)
            scored_events.append(
                ScoredEvent(
                    **event.model_dump(),
                    themes=themes,
                    impact_score=impact,
                    relevance_score=relevance,
                    event_score=total,
                    directional_signal=directional,
                )
            )

        if use_cache:
            async with self._cache_lock:
                self._events_cache_key = cache_key
                self._events_cache_at = datetime.now(timezone.utc)
                self._events_cache = (
                    [event.model_copy(deep=True) for event in scored_events],
                    [health.model_copy(deep=True) for health in source_health],
                )

        return scored_events, source_health

    @staticmethod
    def _trend_label(directional_signal: float) -> str:
        if directional_signal >= 0.02:
            return "bullish"
        if directional_signal <= -0.02:
            return "bearish"
        return "mixed"

    @staticmethod
    def _aggregate_narratives(scored_events: list[ScoredEvent]) -> list[Narrative]:
        grouped: dict[str, list[ScoredEvent]] = defaultdict(list)
        for event in scored_events:
            for theme in event.themes:
                grouped[theme].append(event)

        narratives: list[Narrative] = []
        for theme, events in grouped.items():
            ranked = sorted(events, key=lambda item: item.event_score, reverse=True)
            impact_score = mean(event.impact_score for event in ranked)
            relevance_score = mean(event.relevance_score for event in ranked)
            confidence = mean(event.confidence for event in ranked)
            directional = mean(event.directional_signal for event in ranked)
            event_count = len(ranked)

            # Small breadth bonus for multi-signal narratives.
            breadth_bonus = min(event_count / 30.0, 0.2)
            narrative_score = min((0.6 * impact_score) + (0.4 * relevance_score) + breadth_bonus, 1.0)

            asset_counter = Counter(
                event.asset for event in ranked if event.asset and isinstance(event.asset, str)
            )
            top_assets = [asset for asset, _ in asset_counter.most_common(3)]

            catalysts: list[str] = []
            for event in ranked:
                if event.title not in catalysts:
                    catalysts.append(event.title)
                if len(catalysts) == 3:
                    break

            narratives.append(
                Narrative(
                    theme=theme,
                    narrative_score=round(narrative_score, 4),
                    impact_score=round(impact_score, 4),
                    relevance_score=round(relevance_score, 4),
                    confidence=round(confidence, 4),
                    trend=EagleEyeService._trend_label(directional),
                    event_count=event_count,
                    sources=sorted({event.source for event in ranked}),
                    top_assets=top_assets,
                    catalysts=catalysts,
                    latest_event_at=max(event.timestamp for event in ranked),
                )
            )

        narratives.sort(key=lambda narrative: narrative.narrative_score, reverse=True)
        return narratives

    async def get_snapshot(
        self,
        window_minutes: int | None = None,
        top_narratives: int | None = None,
        source_limit: int | None = None,
    ) -> EagleEyeSnapshot:
        window_minutes = window_minutes or self.config.EAGLE_EYE_WINDOW_MINUTES
        top_narratives = top_narratives or self.config.EAGLE_EYE_TOP_NARRATIVES
        source_limit = source_limit or self.config.EAGLE_EYE_SOURCE_LIMIT

        scored_events, source_health = await self._collect_scored_events(
            window_minutes=window_minutes,
            source_limit=source_limit,
        )
        narratives = self._aggregate_narratives(scored_events)[:top_narratives]

        return EagleEyeSnapshot(
            generated_at=datetime.now(timezone.utc),
            window_minutes=window_minutes,
            events_analyzed=len(scored_events),
            narratives=narratives,
            source_health=source_health,
        )

    async def get_theme_breakdown(
        self,
        theme: str,
        window_minutes: int | None = None,
        event_limit: int = 20,
        source_limit: int | None = None,
    ) -> dict:
        window_minutes = window_minutes or self.config.EAGLE_EYE_WINDOW_MINUTES
        source_limit = source_limit or self.config.EAGLE_EYE_SOURCE_LIMIT
        normalized_theme = theme.strip().lower()

        scored_events, source_health = await self._collect_scored_events(
            window_minutes=window_minutes,
            source_limit=source_limit,
        )
        theme_events = [
            event
            for event in scored_events
            if any(candidate.lower() == normalized_theme for candidate in event.themes)
        ]
        theme_events.sort(key=lambda event: event.event_score, reverse=True)

        return {
            "theme": theme,
            "window_minutes": window_minutes,
            "event_count": len(theme_events),
            "avg_impact_score": round(mean([event.impact_score for event in theme_events]), 4)
            if theme_events
            else 0.0,
            "avg_relevance_score": round(mean([event.relevance_score for event in theme_events]), 4)
            if theme_events
            else 0.0,
            "trend": self._trend_label(mean([event.directional_signal for event in theme_events]))
            if theme_events
            else "mixed",
            "events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "source": event.source,
                    "title": event.title,
                    "asset": event.asset,
                    "score": round(event.event_score, 4),
                    "impact_score": round(event.impact_score, 4),
                    "relevance_score": round(event.relevance_score, 4),
                    "metadata": event.metadata,
                }
                for event in theme_events[:event_limit]
            ],
            "source_health": [status.model_dump(mode="json") for status in source_health],
        }

    async def get_source_health(self, source_limit: int | None = None) -> list[dict]:
        source_limit = source_limit or self.config.EAGLE_EYE_SOURCE_LIMIT
        _, source_health = await self._collect_scored_events(
            window_minutes=self.config.EAGLE_EYE_WINDOW_MINUTES,
            source_limit=source_limit,
            use_cache=True,
        )
        return [item.model_dump(mode="json") for item in source_health]
