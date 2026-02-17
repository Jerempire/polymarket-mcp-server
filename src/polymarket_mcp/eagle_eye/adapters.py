"""Source adapters for Eagle Eye narratives."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from ..config import PolymarketConfig
from ..utils.rate_limiter import EndpointCategory, get_rate_limiter
from .models import SourceEvent

logger = logging.getLogger(__name__)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if isinstance(value, str):
        candidate = value.strip()
        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(candidate)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _extract_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("data", "markets", "items", "results", "tickers"):
            items = payload.get(key)
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        return [payload]
    return []


def _normalize_tags(raw_tags: Any) -> list[str]:
    tags: list[str] = []
    if isinstance(raw_tags, str):
        tags.append(raw_tags)
    elif isinstance(raw_tags, list):
        for item in raw_tags:
            if isinstance(item, str):
                tags.append(item)
            elif isinstance(item, dict):
                label = item.get("name") or item.get("slug") or item.get("label")
                if isinstance(label, str):
                    tags.append(label)
    return tags


class SourceAdapter(ABC):
    """Abstract adapter for a single source."""

    source_name: str

    def __init__(self, config: PolymarketConfig):
        self.config = config

    @abstractmethod
    async def fetch_events(self, limit: int) -> list[SourceEvent]:
        raise NotImplementedError


class PolymarketAdapter(SourceAdapter):
    """Fetch normalized events from the Polymarket API with migration fallback."""

    source_name = "polymarket"

    def _candidate_urls(self) -> list[str]:
        bases = [self.config.POLYMARKET_PRIMARY_API_URL, self.config.POLYMARKET_FALLBACK_API_URL]
        paths = [path.strip() for path in self.config.POLYMARKET_MARKETS_PATHS.split(",") if path.strip()]

        urls: list[str] = []
        for base in bases:
            if not base:
                continue
            normalized_base = base.rstrip("/")
            for path in paths:
                normalized_path = path if path.startswith("/") else f"/{path}"
                urls.append(f"{normalized_base}{normalized_path}")
        return urls

    async def _fetch_markets(self, limit: int) -> list[dict[str, Any]]:
        errors: list[str] = []
        params = {"active": "true", "closed": "false", "limit": limit}

        for url in self._candidate_urls():
            try:
                await get_rate_limiter().acquire(EndpointCategory.GAMMA_API)
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    markets = _extract_items(response.json())
                    if markets:
                        return markets[:limit]
            except Exception as exc:  # pragma: no cover - network failure path
                errors.append(f"{url}: {exc}")

        if errors:
            raise RuntimeError("All Polymarket API variants failed: " + " | ".join(errors[:3]))
        return []

    @staticmethod
    def _extract_probability_change(market: dict[str, Any]) -> float:
        fields = (
            "priceDelta24hr",
            "probability_change_24h",
            "probabilityChange24h",
            "oneDayPriceChange",
            "change24h",
            "delta24hr",
        )
        for field in fields:
            if field in market:
                return _safe_float(market.get(field))
        return 0.0

    @staticmethod
    def _extract_probability(market: dict[str, Any]) -> float:
        prices = market.get("outcomePrices") or market.get("prices")
        if isinstance(prices, str):
            try:
                parsed = json.loads(prices.replace("'", '"'))
                if isinstance(parsed, list) and parsed:
                    return _safe_float(parsed[0])
            except Exception:
                return 0.0
        if isinstance(prices, list) and prices:
            return _safe_float(prices[0])

        tokens = market.get("tokens")
        if isinstance(tokens, list) and tokens:
            first_token = tokens[0]
            if isinstance(first_token, dict):
                return _safe_float(
                    first_token.get("price")
                    or first_token.get("last_price")
                    or first_token.get("bestAsk")
                )
        return 0.0

    async def fetch_events(self, limit: int) -> list[SourceEvent]:
        markets = await self._fetch_markets(limit=limit)
        events: list[SourceEvent] = []

        for index, market in enumerate(markets):
            market_id = str(
                market.get("id")
                or market.get("conditionId")
                or market.get("condition_id")
                or market.get("slug")
                or f"market-{index}"
            )
            title = str(market.get("question") or market.get("title") or f"Market {market_id}")
            summary = market.get("description")
            tags = _normalize_tags(market.get("tags"))
            timestamp = _parse_timestamp(
                market.get("updatedAt")
                or market.get("updated_at")
                or market.get("createdAt")
                or market.get("endDate")
            )

            probability_change = self._extract_probability_change(market)
            probability = self._extract_probability(market)
            volume_24h = _safe_float(
                market.get("volume24hr") or market.get("volume24h") or market.get("volume")
            )
            liquidity = _safe_float(market.get("liquidity"))

            asset = None
            for candidate in (market.get("ticker"), market.get("symbol"), market.get("underlying")):
                if isinstance(candidate, str) and candidate.strip():
                    asset = candidate.strip().upper()
                    break

            impact_hint = min(abs(probability_change) / 0.2, 1.0)
            relevance_hint = min(volume_24h / 2_500_000.0, 1.0)

            events.append(
                SourceEvent(
                    event_id=f"polymarket-{market_id}",
                    source=self.source_name,
                    timestamp=timestamp,
                    title=title,
                    summary=summary,
                    asset=asset,
                    tags=tags + ["polymarket"],
                    impact_hint=impact_hint,
                    relevance_hint=relevance_hint,
                    confidence=0.75,
                    metadata={
                        "market_id": market_id,
                        "probability": probability,
                        "probability_change": probability_change,
                        "volume_24h": volume_24h,
                        "liquidity": liquidity,
                        "url": market.get("url"),
                    },
                )
            )

        return events


class PolygonAdapter(SourceAdapter):
    """Fetch stock/ETF momentum events from Polygon snapshots."""

    source_name = "polygon"

    async def fetch_events(self, limit: int) -> list[SourceEvent]:
        if not self.config.POLYGON_API_KEY:
            return []

        params: dict[str, Any] = {"apiKey": self.config.POLYGON_API_KEY}
        if self.config.POLYGON_TICKERS:
            params["tickers"] = self.config.POLYGON_TICKERS

        await get_rate_limiter().acquire(EndpointCategory.DATA_API)
        endpoint = f"{self.config.POLYGON_API_URL.rstrip('/')}/v2/snapshot/locale/us/markets/stocks/tickers"

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            payload = response.json()

        tickers = _extract_items(payload)
        ranked = sorted(
            tickers,
            key=lambda item: abs(
                _safe_float(item.get("todaysChangePerc") or item.get("day", {}).get("c"))
            ),
            reverse=True,
        )

        events: list[SourceEvent] = []
        for item in ranked[:limit]:
            ticker = str(item.get("ticker") or "").upper()
            day = item.get("day", {}) if isinstance(item.get("day"), dict) else {}
            change_pct = _safe_float(item.get("todaysChangePerc"), _safe_float(day.get("c")))
            volume = _safe_float(day.get("v"))
            close_price = _safe_float(day.get("c"))
            open_price = _safe_float(day.get("o"))
            title = f"{ticker} moved {change_pct:+.2f}% today"

            events.append(
                SourceEvent(
                    event_id=f"polygon-{ticker}",
                    source=self.source_name,
                    timestamp=datetime.now(timezone.utc),
                    title=title,
                    summary="Equity momentum from Polygon snapshot feed",
                    asset=ticker or None,
                    tags=["equities", "polygon"],
                    impact_hint=min(abs(change_pct) / 6.0, 1.0),
                    relevance_hint=min(volume / 50_000_000.0, 1.0),
                    confidence=0.9,
                    metadata={
                        "ticker": ticker,
                        "change_pct": change_pct,
                        "volume_24h": volume,
                        "close": close_price,
                        "open": open_price,
                    },
                )
            )

        return events


class SquawkAdapter(SourceAdapter):
    """Fetch headline/squawk events from URL or local JSON file."""

    source_name = "squawk"

    async def _load_payload(self) -> Any:
        if self.config.SQUAWK_FEED_FILE:
            path = Path(self.config.SQUAWK_FEED_FILE).expanduser()
            if not path.exists():
                raise FileNotFoundError(f"Squawk feed file not found: {path}")
            return json.loads(path.read_text(encoding="utf-8"))

        if not self.config.SQUAWK_FEED_URL:
            return []

        headers: dict[str, str] = {}
        params: dict[str, Any] = {}
        # Prefer explicit squawk key, fall back to market data key for Massive/Polygon shared auth.
        api_key = self.config.SQUAWK_API_KEY or self.config.POLYGON_API_KEY
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            params["apiKey"] = api_key

        await get_rate_limiter().acquire(EndpointCategory.DATA_API)
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(self.config.SQUAWK_FEED_URL, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    async def fetch_events(self, limit: int) -> list[SourceEvent]:
        payload = await self._load_payload()
        items = _extract_items(payload)

        events: list[SourceEvent] = []
        for index, item in enumerate(items[:limit]):
            title = str(item.get("headline") or item.get("title") or item.get("text") or "").strip()
            if not title:
                continue

            symbols = item.get("symbols") or item.get("tickers") or []
            if isinstance(symbols, str):
                symbols = [symbols]
            symbols = [str(symbol).upper() for symbol in symbols if symbol]

            importance_raw = _safe_float(item.get("importance") or item.get("weight") or item.get("priority"))
            importance = importance_raw / 10.0 if importance_raw > 1 else importance_raw

            events.append(
                SourceEvent(
                    event_id=f"squawk-{item.get('id') or index}",
                    source=self.source_name,
                    timestamp=_parse_timestamp(
                        item.get("timestamp")
                        or item.get("published_utc")
                        or item.get("published_at")
                        or item.get("created_utc")
                        or item.get("ts")
                    ),
                    title=title,
                    summary=item.get("summary") or item.get("description") or item.get("body"),
                    asset=symbols[0] if symbols else None,
                    tags=_normalize_tags(item.get("tags")) + ["squawk"],
                    impact_hint=min(max(importance, 0.0), 1.0),
                    relevance_hint=min(max(importance, 0.0), 1.0),
                    confidence=0.72,
                    metadata={
                        "symbols": symbols,
                        "importance": importance,
                        "raw_source": item.get("source"),
                    },
                )
            )

        return events
