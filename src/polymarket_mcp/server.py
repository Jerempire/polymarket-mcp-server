"""
Market Eagle Eye MCP Server - Main entry point.

Provides read-only market discovery, sentiment, and narrative tools via MCP.
"""
import asyncio
import logging
from typing import Any, Dict, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

from .config import load_config, PolymarketConfig
from .utils import get_rate_limiter
from .tools import market_discovery, market_analysis, sentiment_digest, eagle_eye

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
server = Server("market-eagle-eye")
config: Optional[PolymarketConfig] = None


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    tools = []
    tools.extend(market_discovery.get_tools())
    tools.extend(market_analysis.get_tools())
    tools.extend(sentiment_digest.get_tools())
    tools.extend(eagle_eye.get_tools())
    return tools


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="polymarket://status",
            name="Server Status",
            description="Check server status and configuration",
            mimeType="application/json"
        ),
        types.Resource(
            uri="polymarket://rate-limits",
            name="Rate Limiter Status",
            description="Check API rate limit status",
            mimeType="application/json"
        ),
        types.Resource(
            uri="polymarket://eagle-eye-config",
            name="Eagle Eye Config",
            description="Current Eagle Eye source and scoring configuration",
            mimeType="application/json"
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content by URI."""
    import json

    if uri == "polymarket://status":
        status_data = {
            "server_version": "0.3.0",
            "mode": "read-only-eagle-eye",
            "tools_available": 18,
            "gamma_api_url": config.GAMMA_API_URL if config else None,
            "cache_ttl_seconds": config.SENTIMENT_CACHE_TTL_SECONDS if config else None,
        }
        return json.dumps(status_data, indent=2)

    elif uri == "polymarket://rate-limits":
        rate_limiter = get_rate_limiter()
        status = rate_limiter.get_status()
        return json.dumps(status, indent=2)

    elif uri == "polymarket://eagle-eye-config":
        if not config:
            return json.dumps({"error": "Config not loaded"})
        return json.dumps(
            {
                "window_minutes": config.EAGLE_EYE_WINDOW_MINUTES,
                "top_narratives": config.EAGLE_EYE_TOP_NARRATIVES,
                "source_limit": config.EAGLE_EYE_SOURCE_LIMIT,
                "sources": {
                    "polymarket": config.EAGLE_EYE_ENABLE_POLYMARKET,
                    "polygon": config.EAGLE_EYE_ENABLE_POLYGON,
                    "squawk": config.EAGLE_EYE_ENABLE_SQUAWK,
                },
                "polymarket_api": {
                    "primary": config.POLYMARKET_PRIMARY_API_URL,
                    "fallback": config.POLYMARKET_FALLBACK_API_URL,
                    "paths": config.POLYMARKET_MARKETS_PATHS,
                },
            },
            indent=2,
        )

    else:
        return json.dumps({"error": f"Unknown resource: {uri}"})


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[types.TextContent]:
    """Handle tool calls."""
    import json

    try:
        # Market discovery tools (7)
        if name in ["search_markets", "get_trending_markets", "filter_markets_by_category",
                    "get_event_markets", "get_closing_soon_markets",
                    "get_sports_markets", "get_crypto_markets"]:
            return await market_discovery.handle_tool(name, arguments)

        # Market analysis tools (5)
        elif name in ["get_market_details", "get_current_price",
                      "get_market_volume", "get_price_history", "compare_markets"]:
            return await market_analysis.handle_tool(name, arguments)

        # Sentiment digest tools (3)
        elif name in ["get_sentiment_digest", "get_topic_sentiment", "get_biggest_movers"]:
            return await sentiment_digest.handle_tool(name, arguments)

        # Eagle Eye tools (3)
        elif name in ["get_eagle_eye_snapshot", "get_theme_breakdown", "get_source_health"]:
            return await eagle_eye.handle_tool(name, arguments)

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool call failed: {name} - {e}")
        error_result = {
            "success": False,
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        return [
            types.TextContent(
                type="text",
                text=json.dumps(error_result, indent=2)
            )
        ]


async def initialize_server() -> None:
    """Initialize server components: config + rate limiter."""
    global config

    try:
        logger.info("Loading configuration...")
        config = load_config()
        logging.getLogger().setLevel(config.LOG_LEVEL)

        # Initialize rate limiter (singleton)
        get_rate_limiter()
        logger.info("Rate limiter initialized")
        eagle_eye.initialize(config)
        logger.info("Eagle Eye service initialized")

        logger.info("Server initialization complete!")
        logger.info("Mode: READ-ONLY Market Narrative Analysis")
        logger.info("Available tools: 18 (7 Discovery, 5 Analysis, 3 Sentiment, 3 Eagle Eye)")

    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


async def main() -> None:
    """Main entry point for MCP server."""
    try:
        await initialize_server()

        logger.info("Starting MCP server...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


def run():
    """Synchronous entry point for CLI"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
