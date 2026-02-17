"""
Configuration management for the Market Eagle Eye MCP server.
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PolymarketConfig(BaseSettings):
    """
    Configuration settings for Market Eagle Eye MCP server.
    Loads from environment variables with validation.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # API Endpoints
    GAMMA_API_URL: str = Field(
        default="https://gamma-api.polymarket.com",
        description="Gamma API endpoint for market data"
    )
    POLYMARKET_PRIMARY_API_URL: str = Field(
        default="https://gamma-api.polymarket.com",
        description="Primary Polymarket API endpoint (new/active path)"
    )
    POLYMARKET_FALLBACK_API_URL: str = Field(
        default="https://gamma-api.polymarket.com",
        description="Fallback Polymarket API endpoint during API migrations"
    )
    POLYMARKET_MARKETS_PATHS: str = Field(
        default="/markets,/v1/markets",
        description="Comma-separated list of market endpoint paths to try"
    )

    # Polygon market data
    POLYGON_API_URL: str = Field(
        default="https://api.massive.com",
        description="Massive/Polygon API base URL"
    )
    POLYGON_API_KEY: str | None = Field(
        default=None,
        description="Polygon API key for snapshot/momentum data"
    )
    POLYGON_TICKERS: str | None = Field(
        default=None,
        description="Optional comma-separated ticker allowlist for Polygon snapshot"
    )

    # Squawk/headline feed
    SQUAWK_FEED_URL: str | None = Field(
        default="https://api.massive.com/benzinga/v2/news",
        description="HTTP feed URL for squawk/headline events"
    )
    SQUAWK_FEED_FILE: str | None = Field(
        default=None,
        description="Local JSON file path for squawk/headline events"
    )
    SQUAWK_API_KEY: str | None = Field(
        default=None,
        description="Bearer token for the squawk feed URL"
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR"
    )

    # Sentiment Analysis
    SENTIMENT_CACHE_TTL_SECONDS: int = Field(
        default=300,
        description="Cache TTL for sentiment data in seconds"
    )

    # Eagle Eye narrative engine
    EAGLE_EYE_ENABLE_POLYMARKET: bool = Field(
        default=True,
        description="Enable Polymarket source adapter"
    )
    EAGLE_EYE_ENABLE_POLYGON: bool = Field(
        default=True,
        description="Enable Polygon source adapter"
    )
    EAGLE_EYE_ENABLE_SQUAWK: bool = Field(
        default=True,
        description="Enable squawk/headline source adapter"
    )
    EAGLE_EYE_WINDOW_MINUTES: int = Field(
        default=240,
        description="Default lookback window for narratives"
    )
    EAGLE_EYE_TOP_NARRATIVES: int = Field(
        default=12,
        description="Default number of narratives to return"
    )
    EAGLE_EYE_SOURCE_LIMIT: int = Field(
        default=60,
        description="Default events fetched per source per request"
    )
    EAGLE_EYE_CACHE_TTL_SECONDS: int = Field(
        default=20,
        description="In-memory cache TTL for narrative snapshots"
    )

    # Dashboard API
    DASHBOARD_HOST: str = Field(default="127.0.0.1", description="FastAPI dashboard host")
    DASHBOARD_PORT: int = Field(default=8070, description="FastAPI dashboard port")

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v

    @field_validator(
        "EAGLE_EYE_WINDOW_MINUTES",
        "EAGLE_EYE_TOP_NARRATIVES",
        "EAGLE_EYE_SOURCE_LIMIT",
        "EAGLE_EYE_CACHE_TTL_SECONDS",
    )
    @classmethod
    def validate_positive_ints(cls, v: int) -> int:
        """Validate positive integer config values."""
        if v <= 0:
            raise ValueError("Value must be greater than 0")
        return v


def load_config() -> PolymarketConfig:
    """Load configuration from environment variables."""
    return PolymarketConfig()
