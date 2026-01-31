"""
Sentiment Digest Tools for Polymarket MCP Server.

Provides 3 tools for sentiment analysis:
- get_sentiment_digest: Top movers across categories with probability shifts
- get_topic_sentiment: Sentiment for a specific topic
- get_biggest_movers: Markets with largest probability changes
"""
import json
import logging
from typing import Dict, Any, List, Optional
import mcp.types as types
import httpx

from ..utils.rate_limiter import EndpointCategory, get_rate_limiter

logger = logging.getLogger(__name__)

GAMMA_API_URL = "https://gamma-api.polymarket.com"


async def _fetch_active_markets(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch active markets from Gamma API with rate limiting."""
    rate_limiter = get_rate_limiter()
    await rate_limiter.acquire(EndpointCategory.GAMMA_API)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{GAMMA_API_URL}/markets",
            params={"active": "true", "limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        return []


def _extract_probability(market: Dict[str, Any]) -> Optional[float]:
    """Extract current probability (YES price) from market data."""
    # Try outcomePrices first
    prices = market.get("outcomePrices")
    if prices:
        try:
            if isinstance(prices, str):
                import ast
                prices = ast.literal_eval(prices)
            if isinstance(prices, list) and len(prices) > 0:
                return float(prices[0])
        except (ValueError, SyntaxError):
            pass

    # Try bestAsk/bestBid from tokens
    tokens = market.get("tokens", [])
    if tokens and len(tokens) > 0:
        token = tokens[0]
        price = token.get("price")
        if price is not None:
            return float(price)

    return None


def _extract_probability_change(market: Dict[str, Any]) -> Optional[float]:
    """Extract probability change from market data."""
    # Try various fields that might contain change info
    for field in ["priceDelta24hr", "price_change_24h", "delta24hr"]:
        val = market.get(field)
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                pass
    return None


def _categorize_market(market: Dict[str, Any]) -> str:
    """Categorize a market by its tags or question content."""
    tags = market.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    tag_lower = [t.lower() for t in tags if isinstance(t, str)]

    if any(t in tag_lower for t in ["politics", "elections", "government"]):
        return "Politics"
    if any(t in tag_lower for t in ["sports", "nfl", "nba", "soccer", "mlb"]):
        return "Sports"
    if any(t in tag_lower for t in ["crypto", "bitcoin", "ethereum", "defi"]):
        return "Crypto"
    if any(t in tag_lower for t in ["science", "tech", "technology", "ai"]):
        return "Tech & Science"
    if any(t in tag_lower for t in ["entertainment", "culture", "pop culture"]):
        return "Entertainment"
    if any(t in tag_lower for t in ["finance", "economics", "markets"]):
        return "Finance"

    return "Other"


async def get_sentiment_digest(timeframe: str = "24h") -> Dict[str, Any]:
    """
    Top movers across all categories, grouped by topic, showing probability shifts.

    Args:
        timeframe: Time period for analysis ('24h', '7d', '30d')

    Returns:
        Categorized digest of market sentiment with probability changes
    """
    markets = await _fetch_active_markets(limit=100)

    # Enrich with probability data
    enriched = []
    for m in markets:
        prob = _extract_probability(m)
        change = _extract_probability_change(m)
        category = _categorize_market(m)

        volume_key = {"24h": "volume24hr", "7d": "volume7d", "30d": "volume30d"}.get(
            timeframe, "volume24hr"
        )
        volume = float(m.get(volume_key, 0) or 0)

        enriched.append({
            "market_id": m.get("id") or m.get("condition_id", ""),
            "question": m.get("question", ""),
            "probability": prob,
            "probability_change": change,
            "volume": volume,
            "category": category,
            "end_date": m.get("endDate") or m.get("end_date_iso"),
        })

    # Group by category
    categories: Dict[str, List] = {}
    for item in enriched:
        cat = item["category"]
        categories.setdefault(cat, []).append(item)

    # Sort each category by volume descending, take top 5
    digest = {}
    for cat, items in categories.items():
        sorted_items = sorted(items, key=lambda x: x["volume"], reverse=True)
        digest[cat] = sorted_items[:5]

    return {
        "timeframe": timeframe,
        "total_active_markets": len(markets),
        "categories": digest,
    }


async def get_topic_sentiment(topic: str, limit: int = 10) -> Dict[str, Any]:
    """
    Sentiment for a specific topic with current probabilities and changes.

    Args:
        topic: Topic to search for (e.g., "Trump", "Bitcoin", "AI")
        limit: Maximum number of markets to return

    Returns:
        Markets related to the topic with sentiment data
    """
    rate_limiter = get_rate_limiter()
    await rate_limiter.acquire(EndpointCategory.GAMMA_API)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{GAMMA_API_URL}/markets",
            params={"query": topic, "active": "true", "limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            markets = data["data"]
        elif isinstance(data, list):
            markets = data
        else:
            markets = []

    results = []
    for m in markets[:limit]:
        prob = _extract_probability(m)
        change = _extract_probability_change(m)

        results.append({
            "market_id": m.get("id") or m.get("condition_id", ""),
            "question": m.get("question", ""),
            "probability": prob,
            "probability_change": change,
            "volume_24h": float(m.get("volume24hr", 0) or 0),
            "liquidity": float(m.get("liquidity", 0) or 0),
            "end_date": m.get("endDate") or m.get("end_date_iso"),
        })

    # Sort by volume
    results.sort(key=lambda x: x["volume_24h"], reverse=True)

    return {
        "topic": topic,
        "market_count": len(results),
        "markets": results,
    }


async def get_biggest_movers(
    timeframe: str = "24h",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Markets with largest probability changes, sorted by magnitude.

    Args:
        timeframe: Time period ('24h', '7d', '30d')
        limit: Maximum number of markets to return

    Returns:
        Markets sorted by absolute probability change
    """
    markets = await _fetch_active_markets(limit=100)

    movers = []
    for m in markets:
        prob = _extract_probability(m)
        change = _extract_probability_change(m)

        volume_key = {"24h": "volume24hr", "7d": "volume7d", "30d": "volume30d"}.get(
            timeframe, "volume24hr"
        )
        volume = float(m.get(volume_key, 0) or 0)

        movers.append({
            "market_id": m.get("id") or m.get("condition_id", ""),
            "question": m.get("question", ""),
            "probability": prob,
            "probability_change": change,
            "abs_change": abs(change) if change is not None else 0,
            "volume": volume,
            "category": _categorize_market(m),
            "end_date": m.get("endDate") or m.get("end_date_iso"),
        })

    # Sort by absolute change descending
    movers.sort(key=lambda x: x["abs_change"], reverse=True)
    top_movers = movers[:limit]

    # Remove helper field
    for m in top_movers:
        del m["abs_change"]

    return {
        "timeframe": timeframe,
        "total_markets_analyzed": len(markets),
        "movers": top_movers,
    }


def get_tools() -> List[types.Tool]:
    """Get list of sentiment digest tools"""
    return [
        types.Tool(
            name="get_sentiment_digest",
            description="Get a sentiment digest of top movers across all categories, grouped by topic, showing probability shifts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeframe": {
                        "type": "string",
                        "enum": ["24h", "7d", "30d"],
                        "description": "Time period for analysis (default: 24h)",
                        "default": "24h"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_topic_sentiment",
            description="Get sentiment for a specific topic with current probabilities and changes across related markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to search for (e.g., 'Trump', 'Bitcoin', 'AI')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of markets to return (default 10)",
                        "default": 10
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="get_biggest_movers",
            description="Get markets with the largest probability changes, sorted by magnitude of change.",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeframe": {
                        "type": "string",
                        "enum": ["24h", "7d", "30d"],
                        "description": "Time period for change calculation (default: 24h)",
                        "default": "24h"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of markets to return (default 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        )
    ]


async def handle_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution."""
    try:
        if name == "get_sentiment_digest":
            result = await get_sentiment_digest(**arguments)
        elif name == "get_topic_sentiment":
            result = await get_topic_sentiment(**arguments)
        elif name == "get_biggest_movers":
            result = await get_biggest_movers(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        logger.error(f"Tool execution failed for {name}: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]
