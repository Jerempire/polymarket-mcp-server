# 🚀 Quick Start - Real-Time Polymarket Data

## ✅ Setup Complete!

Your environment is ready to go. Here's how to use it:

---

## 📦 Step 1: Activate Virtual Environment

```bash
# On Linux/Mac
source polymarket/bin/activate

# On Windows
polymarket\Scripts\activate
```

---

## 🔧 Step 2: Configuration

Your `.env` file is already set up with **DEMO MODE** enabled:

```bash
DEMO_MODE=true  # No API key needed for read-only access
```

### To Enable Trading (Optional):
Edit `.env` and add your credentials:

```bash
DEMO_MODE=false
POLYGON_PRIVATE_KEY=your_private_key_from_metamask
POLYGON_ADDRESS=0xYourAddressHere
```

**Where to get credentials:**
- MetaMask → Settings → Security & Privacy → Export Private Key
- Your address is shown in MetaMask's main view

---

## 🚀 Step 3: Run Real-Time Data Script

```bash
# Activate venv first
source polymarket/bin/activate

# Run the script
python get_realtime_market_data.py
```

This will show you:
- 📊 Trending markets with live data
- 💰 Current YES/NO probabilities
- 📈 Bid/Ask spreads
- 💧 Volume & Liquidity stats
- 🤖 AI-powered analysis

---

## 📝 Example Code Snippets

### Get Trending Markets

```python
import asyncio
from polymarket_mcp.tools import market_discovery

async def main():
    markets = await market_discovery.get_trending_markets(
        timeframe="24h",
        limit=10
    )

    for market in markets:
        print(f"Question: {market.get('question')}")
        print(f"Volume 24h: ${market.get('volume24hr'):,.0f}")
        print()

asyncio.run(main())
```

### Get Real-Time Prices

```python
import asyncio
from polymarket_mcp.tools import market_analysis

async def get_price(token_id):
    # Get current price (= probability)
    price_data = await market_analysis.get_current_price(
        token_id=token_id,
        side="BOTH"
    )

    probability = price_data.mid * 100  # Convert to percentage
    print(f"Probability: {probability:.1f}%")
    print(f"Bid: ${price_data.bid:.4f}")
    print(f"Ask: ${price_data.ask:.4f}")

# asyncio.run(get_price("your_token_id"))
```

### Search Markets

```python
import asyncio
from polymarket_mcp.tools import market_discovery

async def search(query):
    markets = await market_discovery.search_markets(
        query=query,
        limit=5,
        filters={"active": "true"}
    )

    for market in markets:
        print(market.get('question'))

asyncio.run(search("Bitcoin"))
```

### Monitor Category

```python
import asyncio
from polymarket_mcp.tools import market_discovery

async def monitor_crypto():
    markets = await market_discovery.get_crypto_markets(
        symbol="BTC",
        limit=10
    )

    for market in markets:
        volume = market.get('volume24hr', 0)
        print(f"{market.get('question')}")
        print(f"  Volume: ${volume:,.0f}")

asyncio.run(monitor_crypto())
```

### Get AI Analysis

```python
import asyncio
from polymarket_mcp.tools import market_analysis

async def analyze(market_id):
    analysis = await market_analysis.analyze_market_opportunity(market_id)

    print(f"Question: {analysis.market_question}")
    print(f"Recommendation: {analysis.recommendation}")
    print(f"Confidence: {analysis.confidence_score}%")
    print(f"Risk: {analysis.risk_assessment}")
    print(f"Reasoning: {analysis.reasoning}")

# asyncio.run(analyze("your_market_id"))
```

---

## 📚 Available Tools

### Market Discovery
- `search_markets` - Search by keyword
- `get_trending_markets` - Top volume markets
- `get_crypto_markets` - Crypto markets
- `get_sports_markets` - Sports markets
- `get_closing_soon_markets` - Markets closing soon
- `filter_markets_by_category` - Filter by category
- `get_featured_markets` - Featured markets
- `get_event_markets` - Markets for an event

### Market Analysis
- `get_market_details` - Complete market info
- `get_current_price` - Live bid/ask prices
- `get_orderbook` - Full order book
- `get_spread` - Bid-ask spread
- `get_market_volume` - Volume statistics
- `get_liquidity` - Market liquidity
- `analyze_market_opportunity` - AI analysis
- `compare_markets` - Compare multiple markets

### Real-Time WebSocket
- `subscribe_market_prices` - Live price updates
- `subscribe_orderbook_updates` - Live orderbook
- `get_realtime_status` - Subscription status

---

## 💡 Key Concepts

### Prices = Probabilities
In prediction markets, token prices represent probabilities:
- $0.65 = 65% probability
- $0.35 = 35% probability
- YES + NO ≈ $1.00

### Example
```
Market: "Will Bitcoin hit $100k in 2025?"
YES Price: $0.68 → 68% chance
NO Price: $0.32 → 32% chance
```

---

## 🎯 Common Use Cases

### 1. Monitor Trending Markets
```bash
python get_realtime_market_data.py
```

### 2. Track Specific Markets
```python
asyncio.run(get_realtime_market_data("Trump"))
```

### 3. Compare Markets
```python
from polymarket_mcp.tools import market_analysis

market_ids = ["market_id_1", "market_id_2", "market_id_3"]
comparison = await market_analysis.compare_markets(market_ids)
```

### 4. Find Closing Soon
```python
from polymarket_mcp.tools import market_discovery

closing = await market_discovery.get_closing_soon_markets(hours=24)
```

---

## 🔐 API Key Setup (For Trading)

If you want to enable trading features:

1. **Set DEMO_MODE to false** in `.env`

2. **Add your Polygon wallet credentials**:
   ```bash
   POLYGON_PRIVATE_KEY=your_64_char_private_key
   POLYGON_ADDRESS=0xYourAddressHere
   ```

3. **Optional - Add Polymarket API key**:
   - Visit: https://polymarket.com/settings/api
   - Generate new key
   - Add to `.env`:
     ```bash
     POLYMARKET_API_KEY=your_key
     POLYMARKET_PASSPHRASE=your_passphrase
     POLYMARKET_API_KEY_NAME=your_key_name
     ```

   Or leave empty - the system auto-generates one!

---

## 🛡️ Safety Features

Built-in safety limits (configured in `.env`):

```bash
MAX_ORDER_SIZE_USD=1000           # Max single order
MAX_TOTAL_EXPOSURE_USD=5000       # Max total exposure
MAX_POSITION_SIZE_PER_MARKET=2000 # Max per market
MIN_LIQUIDITY_REQUIRED=10000      # Min liquidity needed
MAX_SPREAD_TOLERANCE=0.05         # Max 5% spread
```

---

## 🆘 Troubleshooting

### Issue: Command not found
```bash
source polymarket/bin/activate
```

### Issue: Import errors
```bash
pip install -e .
```

### Issue: API 403 Forbidden
- Check network/firewall
- Try a VPN
- Ensure no proxy blocking requests

### Issue: Rate limited
Built-in rate limiting handles this automatically

---

## 📖 More Resources

- **Full Examples**: `USAGE_EXAMPLES.py`
- **Live Demo**: `demo_mcp_tools.py`
- **Polymarket Docs**: https://docs.polymarket.com

---

## ✅ You're All Set!

```bash
# 1. Activate venv
source polymarket/bin/activate

# 2. Run the script
python get_realtime_market_data.py

# 3. Or run examples
python USAGE_EXAMPLES.py

# 4. Or run demo
python demo_mcp_tools.py
```

**No API key needed for market data viewing!** 🎉

The `.env` file is configured for **DEMO MODE** - you can view all market data without any credentials.
