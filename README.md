# Polymarket Sentiment Analysis MCP Server

Read-only MCP server providing 15 tools for Polymarket sentiment analysis, market discovery, and market data. No wallet, no trading, no authentication required.

## Tools (15)

### Market Discovery (7)
- `search_markets` - Search by text/keywords
- `get_trending_markets` - Highest volume markets
- `filter_markets_by_category` - Filter by category tag
- `get_event_markets` - All markets for an event
- `get_featured_markets` - Featured/promoted markets
- `get_closing_soon_markets` - Markets closing soon
- `get_sports_markets` / `get_crypto_markets` - Domain-specific

### Market Analysis (5)
- `get_market_details` - Full market metadata
- `get_current_price` - Bid/ask prices
- `get_market_volume` - Volume across timeframes
- `get_price_history` - Historical data (limited)
- `compare_markets` - Side-by-side comparison

### Sentiment Digest (3)
- `get_sentiment_digest` - Top movers by category with probability shifts
- `get_topic_sentiment` - Sentiment for a specific topic
- `get_biggest_movers` - Largest probability changes

## Setup

```bash
pip install -e .
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "polymarket-sentiment": {
      "command": "polymarket-mcp",
      "env": {
        "LOG_LEVEL": "INFO",
        "SENTIMENT_CACHE_TTL_SECONDS": "300"
      }
    }
  }
}
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log verbosity |
| `SENTIMENT_CACHE_TTL_SECONDS` | `300` | Cache TTL for sentiment data |

## License

See [LICENSE](LICENSE).
