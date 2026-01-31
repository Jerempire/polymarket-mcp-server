# Polymarket MCP Server - Sentiment Analysis Refactor

## What Changed

Stripped the 45-tool trading platform down to a 15-tool read-only sentiment/news analysis server.

## Removed
- **Auth module** (`auth/`) - wallet, signing, CLOB client
- **Trading tools** - order creation, management, smart trading
- **Portfolio tools** - positions, PnL, risk analysis
- **Realtime tools** - WebSocket subscriptions
- **Safety limits** - order validation, risk management
- **WebSocket manager** - live data feeds
- **Web dashboard** - FastAPI dashboard + templates
- **Infrastructure** - Dockerfile, docker-compose, k8s/, Makefile, install scripts
- **30+ docs/scripts** - trading guides, test scripts, setup wizards

## Kept & Trimmed
- **Market Discovery** (7 tools) - removed `get_featured_markets`
- **Market Analysis** (5 tools) - removed `get_orderbook`, `get_spread`, `get_liquidity`, `get_market_holders`, `analyze_market_opportunity`
- **Rate limiter** - kept as-is for API protection

## Added
- **Sentiment Digest** (3 new tools):
  - `get_sentiment_digest` - categorized overview of top movers
  - `get_topic_sentiment` - topic-specific sentiment with probabilities
  - `get_biggest_movers` - markets with largest probability changes

## Config Changes
- Removed: wallet keys, trading limits, trading controls, contract addresses, CLOB config
- Kept: `GAMMA_API_URL`, `LOG_LEVEL`
- Added: `SENTIMENT_CACHE_TTL_SECONDS`

## Dependencies
- Removed: `py-clob-client`, `eth-account`, `websockets`, `fastapi`, `uvicorn`, `jinja2`
- Kept: `mcp`, `httpx`, `pydantic`, `pydantic-settings`, `python-dotenv`

## Version
- `0.1.0` (trading) -> `0.2.0` (sentiment analysis)
