# 🚀 START HERE - Polymarket MCP Server

**Your Location:** `C:\Users\jmj2z\Projects\polymarket-mcp-server`

---

## ⚡ Quick Start (3 Minutes)

### 1. Open Command Prompt
```cmd
Win + R → type "cmd" → Enter
```

### 2. Run These Commands
```cmd
cd C:\Users\jmj2z\Projects\polymarket-mcp-server
python -m venv polymarket
polymarket\Scripts\activate
pip install -e .
python get_realtime_market_data.py
```

**That's it!** 🎉

---

## 📚 What You Get

### ✅ **NO API KEY NEEDED** for Read-Only Mode

Your `.env` file is already configured with `DEMO_MODE=true`

You can:
- ✅ View real-time market prices & probabilities
- ✅ Search and discover markets
- ✅ Get trading volume & liquidity data
- ✅ View orderbook data
- ✅ Get AI-powered market analysis
- ✅ Track trending markets

You **cannot** (without API key):
- ❌ Place trades
- ❌ Manage portfolio
- ❌ Execute orders

---

## 🔑 Want to Enable Trading?

**Edit:** `C:\Users\jmj2z\Projects\polymarket-mcp-server\.env`

1. Change line 7: `DEMO_MODE=false`
2. Uncomment line 16: `POLYGON_PRIVATE_KEY=your_key_here`
3. Uncomment line 20: `POLYGON_ADDRESS=0xYourAddress`

**Get keys from:**
- Open MetaMask
- Settings → Security & Privacy → Export Private Key
- Your address is in MetaMask main view

---

## 📖 Documentation Guide

| File | Use Case |
|------|----------|
| **WINDOWS_SETUP.md** | Windows-specific setup (YOUR GUIDE) |
| **QUICK_START.md** | Quick reference for all commands |
| **LOCAL_SETUP.md** | Detailed setup for Mac/Linux/Windows |
| **.env** | Configuration file (API keys go here) |
| **get_realtime_market_data.py** | Main script to run |

---

## 🎯 Common Tasks

### View Trending Markets
```cmd
polymarket\Scripts\activate
python get_realtime_market_data.py
```

### Search Specific Markets
Edit `get_realtime_market_data.py` line 210:
```python
await get_realtime_market_data("Bitcoin")  # Search for Bitcoin markets
```

### Run Examples
```cmd
python USAGE_EXAMPLES.py
```

### Run Demo
```cmd
python demo_mcp_tools.py
```

---

## 🔧 Daily Workflow

### First Time Setup (Once)
```cmd
cd C:\Users\jmj2z\Projects\polymarket-mcp-server
python -m venv polymarket
polymarket\Scripts\activate
pip install -e .
```

### Every Time You Use It
```cmd
cd C:\Users\jmj2z\Projects\polymarket-mcp-server
polymarket\Scripts\activate
python get_realtime_market_data.py
```

### When Done
```cmd
deactivate
```

---

## 🆘 Troubleshooting

### Error: "python is not recognized"
```cmd
py -m venv polymarket
py get_realtime_market_data.py
```

### Error: Can't activate polymarket
Using PowerShell? Try:
```powershell
polymarket\Scripts\Activate.ps1
```

### Error: "Module not found"
```cmd
polymarket\Scripts\activate
pip install -e .
```

### Error: Can't find .env file
1. File Explorer → `C:\Users\jmj2z\Projects\polymarket-mcp-server`
2. View tab → Check "Hidden items" and "File name extensions"

---

## 📊 Example Output

When you run `python get_realtime_market_data.py`, you'll see:

```
🔥 EXAMPLE 1: Trending Markets with Real-Time Data
================================================================================
📊 REAL-TIME POLYMARKET DATA
================================================================================

🔥 Getting trending markets...
✅ Found 5 markets

================================================================================
📈 MARKET #1: Will Trump win 2024 election?
================================================================================

📋 BASIC INFO:
  Market ID: 0x1234...
  Active: ✅ Yes
  Category: Politics

💰 CURRENT PROBABILITIES:
  YES: 68.5% ($0.6850)
    ├─ Bid: $0.6830
    └─ Ask: $0.6870
  NO:  31.5% ($0.3150)
    ├─ Bid: $0.3140
    └─ Ask: $0.3160

  📊 Spread: 0.58%

📊 TRADING VOLUME:
  24h:  $1,234,567.89
  7d:   $8,765,432.10
  30d:  $25,432,109.87

💧 LIQUIDITY: $2,345,678.90

🤖 AI ANALYSIS:
  Recommendation: BUY
  Confidence: 75%
  Risk Level: MEDIUM
  Reasoning: Strong volume and tight spread indicate healthy market...
```

---

## 🎓 Learn More

### Code Examples
Check `USAGE_EXAMPLES.py` for comprehensive examples of:
- Market discovery
- Price analysis
- AI-powered analysis
- Portfolio management (with API key)
- Trading (with API key)

### API Reference
- Market Discovery: 8 tools
- Market Analysis: 10 tools
- Real-Time WebSocket: 6 tools
- Portfolio Management: 8 tools (requires API key)
- Trading: 9 tools (requires API key)

---

## ✅ Verification Checklist

- [ ] Opened Command Prompt
- [ ] Navigated to `C:\Users\jmj2z\Projects\polymarket-mcp-server`
- [ ] Created virtual environment: `python -m venv polymarket`
- [ ] Activated it: `polymarket\Scripts\activate`
- [ ] Saw `(polymarket)` in command prompt
- [ ] Installed: `pip install -e .`
- [ ] Ran script: `python get_realtime_market_data.py`
- [ ] Saw real market data appear

---

## 🎯 What's Next?

### Just Exploring?
- Run the main script to see trending markets
- Try searching for specific topics
- Check out the AI analysis recommendations

### Want to Trade?
- Add your MetaMask credentials to `.env`
- Set `DEMO_MODE=false`
- Review safety limits in `.env`
- Start with small test trades

### Building Something?
- Check `USAGE_EXAMPLES.py` for code patterns
- Review the tool documentation
- Build your own analysis scripts
- Create automated strategies

---

## 💡 Pro Tips

1. **Keep polymarket activated** - Always activate before running scripts
2. **Use DEMO_MODE first** - Test everything before adding real credentials
3. **Check safety limits** - Review `MAX_ORDER_SIZE_USD` and other limits in `.env`
4. **Monitor the logs** - Set `LOG_LEVEL=DEBUG` in `.env` for detailed output
5. **Update regularly** - `git pull` to get latest features

---

## 📞 Need Help?

- **Windows Guide:** `WINDOWS_SETUP.md`
- **Quick Reference:** `QUICK_START.md`
- **Full Guide:** `LOCAL_SETUP.md`
- **Code Examples:** `USAGE_EXAMPLES.py`
- **GitHub Issues:** https://github.com/Jerempire/polymarket-mcp-server/issues

---

## 🔒 Security Reminders

- ✅ Never commit `.env` to git (already in `.gitignore`)
- ✅ Keep your private key secret
- ✅ Use safety limits in `.env`
- ✅ Start with DEMO_MODE
- ✅ Test on testnet first (`POLYMARKET_CHAIN_ID=80002`)

---

**Ready to see real-time prediction market data?**

```cmd
cd C:\Users\jmj2z\Projects\polymarket-mcp-server
polymarket\Scripts\activate
python get_realtime_market_data.py
```

**Let's go!** 🚀
