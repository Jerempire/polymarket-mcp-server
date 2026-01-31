"""
Market Analysis Tools for Polymarket MCP Server.

Provides 5 tools for analyzing markets:
- get_market_details: Complete market information
- get_current_price: Current bid/ask prices
- get_market_volume: Volume statistics
- get_price_history: Historical price data
- compare_markets: Compare multiple markets
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import mcp.types as types
import httpx

from ..utils.rate_limiter import EndpointCategory, get_rate_limiter

logger = logging.getLogger(__name__)

# API URLs
GAMMA_API_URL = "https://gamma-api.polymarket.com"
CLOB_API_URL = "https://clob.polymarket.com"


class PriceData(BaseModel):
    """Price information for a token"""
    token_id: str
    bid: Optional[float] = None
    ask: Optional[float] = None
    mid: Optional[float] = None
    last: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VolumeData(BaseModel):
    """Volume statistics"""
    market_id: str
    volume_24h: Optional[float] = None
    volume_7d: Optional[float] = None
    volume_30d: Optional[float] = None
    volume_all_time: Optional[float] = None


async def _fetch_gamma_api(endpoint: str, params: Optional[Dict] = None) -> Any:
    """Fetch from Gamma API with rate limiting"""
    rate_limiter = get_rate_limiter()
    await rate_limiter.acquire(EndpointCategory.GAMMA_API)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{GAMMA_API_URL}{endpoint}"
            response = await client.get(url, params=params or {})
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Gamma API error for {endpoint}: {e}")
        raise


async def _fetch_clob_api(endpoint: str, params: Optional[Dict] = None) -> Any:
    """Fetch from CLOB API with rate limiting"""
    rate_limiter = get_rate_limiter()
    await rate_limiter.acquire(EndpointCategory.MARKET_DATA)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{CLOB_API_URL}{endpoint}"
            response = await client.get(url, params=params or {})
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"CLOB API error for {endpoint}: {e}")
        raise


async def get_market_details(
    market_id: Optional[str] = None,
    condition_id: Optional[str] = None,
    slug: Optional[str] = None
) -> Dict[str, Any]:
    """Get complete market information."""
    try:
        if slug:
            data = await _fetch_gamma_api(f"/markets/{slug}")
        elif condition_id:
            data = await _fetch_gamma_api(f"/markets", {"condition_id": condition_id})
        elif market_id:
            data = await _fetch_gamma_api(f"/markets/{market_id}")
        else:
            raise ValueError("One of market_id, condition_id, or slug must be provided")

        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data

    except Exception as e:
        logger.error(f"Failed to get market details: {e}")
        raise


async def get_current_price(token_id: str, side: str = "BOTH") -> PriceData:
    """Get current bid/ask prices."""
    try:
        price_data = PriceData(token_id=token_id)

        if side in ["BUY", "BOTH"]:
            buy_data = await _fetch_clob_api("/price", {"token_id": token_id, "side": "BUY"})
            price_data.ask = float(buy_data.get("price", 0))

        if side in ["SELL", "BOTH"]:
            sell_data = await _fetch_clob_api("/price", {"token_id": token_id, "side": "SELL"})
            price_data.bid = float(sell_data.get("price", 0))

        if price_data.bid is not None and price_data.ask is not None:
            price_data.mid = (price_data.bid + price_data.ask) / 2.0

        return price_data

    except Exception as e:
        logger.error(f"Failed to get current price: {e}")
        raise


async def get_market_volume(
    market_id: str,
    timeframes: Optional[List[str]] = None
) -> VolumeData:
    """Get volume statistics."""
    try:
        market_data = await get_market_details(market_id=market_id)

        volume_data = VolumeData(market_id=market_id)
        volume_data.volume_24h = float(market_data.get("volume24hr", 0) or 0)
        volume_data.volume_7d = float(market_data.get("volume7d", 0) or 0)
        volume_data.volume_30d = float(market_data.get("volume30d", 0) or 0)
        volume_data.volume_all_time = float(market_data.get("volumeNum", 0) or 0)

        return volume_data

    except Exception as e:
        logger.error(f"Failed to get market volume: {e}")
        raise


async def get_price_history(
    token_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    resolution: str = "1h"
) -> List[Dict[str, Any]]:
    """Get historical price data."""
    try:
        logger.warning(
            "Historical price data not available via public API. "
            "Consider using a third-party data provider."
        )
        return [{
            "error": "Historical price data not available via public Polymarket API",
            "suggestion": "Use real-time price tracking or third-party data providers"
        }]

    except Exception as e:
        logger.error(f"Failed to get price history: {e}")
        raise


async def compare_markets(market_ids: List[str]) -> List[Dict[str, Any]]:
    """Compare multiple markets."""
    try:
        if len(market_ids) < 2:
            raise ValueError("At least 2 markets required for comparison")
        if len(market_ids) > 10:
            raise ValueError("Maximum 10 markets can be compared at once")

        comparisons = []
        for market_id in market_ids:
            try:
                market = await get_market_details(market_id=market_id)
                volume = await get_market_volume(market_id)
                comparisons.append({
                    "market_id": market_id,
                    "question": market.get("question", "Unknown"),
                    "volume_24h": volume.volume_24h,
                    "volume_7d": volume.volume_7d,
                    "liquidity_usd": float(market.get("liquidity", 0) or 0),
                    "end_date": market.get("endDate") or market.get("end_date_iso"),
                    "active": market.get("active", True),
                    "tags": market.get("tags", [])
                })
            except Exception as market_error:
                logger.warning(f"Failed to fetch data for {market_id}: {market_error}")
                comparisons.append({"market_id": market_id, "error": str(market_error)})

        return comparisons

    except Exception as e:
        logger.error(f"Failed to compare markets: {e}")
        raise


def get_tools() -> List[types.Tool]:
    """Get list of market analysis tools"""
    return [
        types.Tool(
            name="get_market_details",
            description="Get complete market information including metadata, tokens, volume, and liquidity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "market_id": {"type": "string", "description": "Market ID"},
                    "condition_id": {"type": "string", "description": "Condition ID (alternative identifier)"},
                    "slug": {"type": "string", "description": "Market slug (alternative identifier)"}
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_current_price",
            description="Get current bid/ask prices for a token.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_id": {"type": "string", "description": "Token ID"},
                    "side": {
                        "type": "string",
                        "enum": ["BUY", "SELL", "BOTH"],
                        "description": "Price side to fetch (default: BOTH)",
                        "default": "BOTH"
                    }
                },
                "required": ["token_id"]
            }
        ),
        types.Tool(
            name="get_market_volume",
            description="Get volume statistics for different timeframes (24h, 7d, 30d, all-time).",
            inputSchema={
                "type": "object",
                "properties": {
                    "market_id": {"type": "string", "description": "Market ID"},
                    "timeframes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of timeframes (default: ['24h', '7d', '30d'])"
                    }
                },
                "required": ["market_id"]
            }
        ),
        types.Tool(
            name="get_price_history",
            description="Get historical price data (OHLC). Note: Limited availability via public API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_id": {"type": "string", "description": "Token ID"},
                    "start_date": {"type": "string", "description": "Start date (ISO format)"},
                    "end_date": {"type": "string", "description": "End date (ISO format)"},
                    "resolution": {
                        "type": "string",
                        "enum": ["1m", "5m", "1h", "1d"],
                        "description": "Time resolution (default: 1h)",
                        "default": "1h"
                    }
                },
                "required": ["token_id"]
            }
        ),
        types.Tool(
            name="compare_markets",
            description="Compare multiple markets side-by-side with key metrics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "market_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of market IDs to compare (2-10 markets)"
                    }
                },
                "required": ["market_ids"]
            }
        )
    ]


async def handle_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution."""
    try:
        if name == "get_market_details":
            result = await get_market_details(**arguments)
        elif name == "get_current_price":
            result = await get_current_price(**arguments)
            result = result.model_dump(mode='json')
        elif name == "get_market_volume":
            result = await get_market_volume(**arguments)
            result = result.model_dump(mode='json')
        elif name == "get_price_history":
            result = await get_price_history(**arguments)
        elif name == "compare_markets":
            result = await compare_markets(**arguments)
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
