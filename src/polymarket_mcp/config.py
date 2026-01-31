"""
Configuration management for Polymarket Sentiment Analysis MCP server.
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PolymarketConfig(BaseSettings):
    """
    Configuration settings for Polymarket Sentiment Analysis MCP server.
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

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v


def load_config() -> PolymarketConfig:
    """Load configuration from environment variables."""
    return PolymarketConfig()
