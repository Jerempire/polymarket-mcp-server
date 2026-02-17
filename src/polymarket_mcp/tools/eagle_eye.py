"""MCP tools for Eagle Eye narrative ranking."""

from __future__ import annotations

import json
import logging
from typing import Any

import mcp.types as types

from ..config import PolymarketConfig
from ..eagle_eye import EagleEyeService

logger = logging.getLogger(__name__)

_service: EagleEyeService | None = None


def initialize(config: PolymarketConfig) -> None:
    """Initialize Eagle Eye service with runtime config."""
    global _service
    _service = EagleEyeService(config)


def _get_service() -> EagleEyeService:
    if _service is None:
        raise RuntimeError("Eagle Eye service not initialized")
    return _service


def get_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_eagle_eye_snapshot",
            description=(
                "Get ranked market narratives/themes across Polymarket, Polygon, and Squawk-like feeds. "
                "Each narrative is scored by impact and relevance."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "window_minutes": {
                        "type": "integer",
                        "description": "Lookback window in minutes (default from config)",
                    },
                    "top_narratives": {
                        "type": "integer",
                        "description": "Maximum number of narratives returned",
                    },
                    "source_limit": {
                        "type": "integer",
                        "description": "Max events fetched per source",
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get_theme_breakdown",
            description=(
                "Get event-level breakdown for a specific theme with source, impact, relevance, and supporting "
                "catalysts."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "theme": {"type": "string", "description": "Theme name from snapshot output"},
                    "window_minutes": {"type": "integer", "description": "Lookback window in minutes"},
                    "event_limit": {"type": "integer", "description": "Maximum events to return", "default": 20},
                    "source_limit": {"type": "integer", "description": "Max events fetched per source"},
                },
                "required": ["theme"],
            },
        ),
        types.Tool(
            name="get_source_health",
            description="Check source ingestion health, event counts, and latency by source.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_limit": {"type": "integer", "description": "Max events fetched per source"},
                },
                "required": [],
            },
        ),
    ]


async def handle_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    service = _get_service()

    try:
        if name == "get_eagle_eye_snapshot":
            snapshot = await service.get_snapshot(**arguments)
            result = snapshot.model_dump(mode="json")
        elif name == "get_theme_breakdown":
            result = await service.get_theme_breakdown(**arguments)
        elif name == "get_source_health":
            result = await service.get_source_health(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as exc:
        logger.error("Eagle Eye tool failed (%s): %s", name, exc)
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(exc), "tool": name}, indent=2),
            )
        ]

