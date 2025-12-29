# 💻 Local Machine Setup Guide

## The network restrictions in this environment prevent API calls, but everything will work perfectly on your local machine!

---

## 🚀 Step-by-Step Setup on Your Computer

### Step 1: Clone/Download the Repository

```bash
# If you haven't already, clone the repository
git clone https://github.com/Jerempire/polymarket-mcp-server.git
cd polymarket-mcp-server

# Or pull the latest changes
git pull origin claude/read-review-code-i19iC
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv polymarket

# Activate it
# On Mac/Linux:
source polymarket/bin/activate

# On Windows:
polymarket\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install the package
pip install -e .
```

### Step 4: Configure Your API Keys

Edit the `.env` file in the project root:

```bash
# Option A: Keep DEMO MODE for read-only access (NO API KEY NEEDED)
DEMO_MODE=true
```

**OR**

```bash
# Option B: Enable trading (REQUIRES API KEY)
DEMO_MODE=false

# Uncomment and add your credentials:
POLYGON_PRIVATE_KEY=your_64_char_private_key_here
POLYGON_ADDRESS=0xYourAddressHere
```

#### Where to Get Your API Keys:

**POLYGON_PRIVATE_KEY & POLYGON_ADDRESS:**
1. Open MetaMask wallet
2. Click on your account → Settings
3. Security & Privacy → Export Private Key
4. Enter password and copy the key (64 characters)
5. Your address is shown in MetaMask main view (starts with 0x)

**POLYMARKET_API_KEY (Optional):**
1. Visit: https://polymarket.com/settings/api
2. Click "Generate New API Key"
3. Copy the key, passphrase, and name
4. Add to `.env` file

**OR** leave empty - the system will auto-generate one for you!

### Step 5: Run the Real-Time Data Script

```bash
# Make sure polymarket env is activated
source polymarket/bin/activate

# Run the script
python get_realtime_market_data.py
```

**OR**

```bash
# Use the easy run script
./run.sh
```

---

## 📂 File Structure

```
polymarket-mcp-server/
├── .env                          ← YOUR API KEYS GO HERE
├── get_realtime_market_data.py   ← Main script to run
├── run.sh                         ← Easy run script
├── QUICK_START.md                 ← Quick reference
├── polymarket/                          ← Virtual environment
└── src/polymarket_mcp/
    └── tools/
        ├── market_discovery.py    ← Market search tools
        ├── market_analysis.py     ← Price & analysis tools
        └── realtime.py            ← WebSocket tools
```

---

## 🔑 What to Put in `.env` File

### For Read-Only Access (View Market Data):
```bash
DEMO_MODE=true
```
**That's it! No API key needed.**

### For Trading Access:
```bash
DEMO_MODE=false

# Add these lines (uncomment the #):
POLYGON_PRIVATE_KEY=abc123def456...  # 64 hex characters
POLYGON_ADDRESS=0x1234567890...       # Your wallet address

# Optional (auto-generated if empty):
POLYMARKET_API_KEY=
POLYMARKET_PASSPHRASE=
POLYMARKET_API_KEY_NAME=
```

---

## ✅ Verify It Works

After setup, test with:

```bash
python get_realtime_market_data.py
```

You should see:
```
📊 REAL-TIME POLYMARKET DATA
================================================================================

🔥 Getting trending markets...
✅ Found 5 markets

📈 MARKET #1: Will Trump win 2024 election?
  YES: 68.5% ($0.6850)
  NO:  31.5% ($0.3150)
  Volume 24h: $1,234,567
  ...
```

---

## 🎯 Quick Examples

### Example 1: Get Trending Markets
```python
import asyncio
from polymarket_mcp.tools import market_discovery

async def main():
    markets = await market_discovery.get_trending_markets(limit=10)
    for m in markets:
        print(f"{m.get('question')}: ${m.get('volume24hr'):,.0f}")

asyncio.run(main())
```

### Example 2: Search Markets
```python
import asyncio
from polymarket_mcp.tools import market_discovery

async def main():
    markets = await market_discovery.search_markets("Bitcoin", limit=5)
    for m in markets:
        print(m.get('question'))

asyncio.run(main())
```

### Example 3: Get Real-Time Price
```python
import asyncio
from polymarket_mcp.tools import market_analysis

async def main():
    price = await market_analysis.get_current_price(
        token_id="your_token_id",
        side="BOTH"
    )

    probability = price.mid * 100
    print(f"Probability: {probability:.1f}%")
    print(f"Bid: ${price.bid:.4f}")
    print(f"Ask: ${price.ask:.4f}")

asyncio.run(main())
```

---

## 🆘 Troubleshooting

### Issue: "Module not found"
```bash
source polymarket/bin/activate
pip install -e .
```

### Issue: "POLYGON_PRIVATE_KEY required"
Either:
1. Set `DEMO_MODE=true` in `.env` (no trading)
2. Add your private key to `.env`

### Issue: "403 Forbidden" or Network Error
- You're probably in the sandboxed environment
- Run on your local machine instead
- Check firewall/antivirus settings
- Try a different network if needed

### Issue: Can't find `.env` file
The file is in the project root:
```bash
cd polymarket-mcp-server
ls -la .env
```

If it doesn't exist, copy from example:
```bash
cp .env.example .env
```

---

## 🔐 Security Tips

1. **Never commit `.env` to git** - it's already in `.gitignore`
2. **Keep your private key secret** - treat it like a password
3. **Use safety limits** - configured in `.env` file
4. **Start with DEMO MODE** - test everything before trading
5. **Use testnet first** - set `POLYMARKET_CHAIN_ID=80002`

---

## 📊 What You Can Access

### With DEMO MODE (No API Key):
✅ Real-time market prices
✅ Market probabilities
✅ Trading volume & liquidity
✅ Orderbook data
✅ Market search & discovery
✅ AI-powered analysis
✅ Trending markets
✅ Category filtering

### With API Key (Trading Enabled):
✅ All of the above, PLUS:
✅ Place trades
✅ Manage positions
✅ Track portfolio P&L
✅ Cancel orders
✅ Automated strategies

---

## 🎉 You're Ready!

**On your local machine:**

1. ✅ Pull the code
2. ✅ Create polymarket environment
3. ✅ Install dependencies
4. ✅ Edit `.env` file
5. ✅ Run `python get_realtime_market_data.py`

**No network restrictions on your machine!** 🚀

---

## 📚 Additional Files to Check

- `QUICK_START.md` - Quick reference guide
- `USAGE_EXAMPLES.py` - Comprehensive code examples
- `demo_mcp_tools.py` - Live demo script
- `.env.example` - Template configuration file

---

**Questions?** Check the README.md or open an issue on GitHub!
