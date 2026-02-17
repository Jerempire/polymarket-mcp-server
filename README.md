# Market Eagle Eye MCP Server

Read-only MCP + dashboard backend for current market narratives and themes, weighted by impact and relevance.

This project extends the original Polymarket sentiment server with:
- multi-source ingestion adapters (Polymarket, Polygon, Squawk-style feed)
- API migration fallback layer for Polymarket endpoint changes
- narrative scoring engine (impact + relevance)
- dashboard-ready API and lightweight web UI

## Tools (18)

### Existing Polymarket Tooling (15)
- Market discovery (7)
- Market analysis (5)
- Sentiment digest (3)

### Eagle Eye Tools (3)
- `get_eagle_eye_snapshot` - ranked narratives/themes for the current window
- `get_theme_breakdown` - event-level support for a selected theme
- `get_source_health` - source ingestion status and latency

## Quick Start

```bash
pip install -e .
```

Run MCP server:

```bash
market-eagle-eye-mcp
```

Run dashboard API/UI:

```bash
market-eagle-eye-dashboard
```

Dashboard default URL: `http://127.0.0.1:8070`

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "market-eagle-eye": {
      "command": "market-eagle-eye-mcp",
      "env": {
        "LOG_LEVEL": "INFO",
        "EAGLE_EYE_WINDOW_MINUTES": "240",
        "EAGLE_EYE_TOP_NARRATIVES": "12"
      }
    }
  }
}
```

## Key Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `POLYMARKET_PRIMARY_API_URL` | `https://gamma-api.polymarket.com` | Primary Polymarket base URL |
| `POLYMARKET_FALLBACK_API_URL` | `https://gamma-api.polymarket.com` | Fallback Polymarket base URL |
| `POLYMARKET_MARKETS_PATHS` | `/markets,/v1/markets` | Endpoint path fallback list |
| `POLYGON_API_URL` | `https://api.massive.com` | Massive/Polygon API base URL |
| `POLYGON_API_KEY` | unset | Enables market-data adapter when set |
| `SQUAWK_FEED_URL` / `SQUAWK_FEED_FILE` | `https://api.massive.com/benzinga/v2/news` / unset | Squawk/news feed source |
| `EAGLE_EYE_WINDOW_MINUTES` | `240` | Default lookback window |
| `EAGLE_EYE_TOP_NARRATIVES` | `12` | Default ranked narratives output |
| `EAGLE_EYE_SOURCE_LIMIT` | `60` | Max events per source pull |
| `EAGLE_EYE_CACHE_TTL_SECONDS` | `20` | Cache TTL to reduce repeated API calls |

## License

See `LICENSE`.
