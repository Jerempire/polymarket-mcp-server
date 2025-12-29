# ✅ Windows Setup Verification Checklist

## 📍 Your Location:
```
C:\Users\jmj2z\Projects\polymarket-mcp-server
```

---

## 🔧 Step-by-Step Windows Setup

### Step 1: Open Command Prompt

1. Press `Win + R`
2. Type `cmd` and press Enter
3. Navigate to your project:

```cmd
cd C:\Users\jmj2z\Projects\polymarket-mcp-server
```

---

### Step 2: Verify Files Are Present

Check these files exist:

```cmd
dir
```

You should see:
- ✅ `.env` - Configuration file
- ✅ `get_realtime_market_data.py` - Main script
- ✅ `QUICK_START.md` - Quick guide
- ✅ `LOCAL_SETUP.md` - Full setup guide
- ✅ `run.sh` - Linux/Mac script (won't work on Windows)
- ✅ `src\` - Source code folder

---

### Step 3: Create Virtual Environment

```cmd
python -m venv polymarket
```

This creates a folder called `polymarket\` in your project directory.

---

### Step 4: Activate Virtual Environment

```cmd
polymarket\Scripts\activate
```

**You should see `(polymarket)` appear at the start of your command prompt!**

Example:
```
(polymarket) C:\Users\jmj2z\Projects\polymarket-mcp-server>
```

---

### Step 5: Install Dependencies

With polymarket activated:

```cmd
pip install --upgrade pip
pip install -e .
```

Wait for installation to complete...

---

### Step 6: Configure API Keys (Optional)

**Location of .env file:**
```
C:\Users\jmj2z\Projects\polymarket-mcp-server\.env
```

**To edit:**

1. Open File Explorer
2. Go to: `C:\Users\jmj2z\Projects\polymarket-mcp-server`
3. Right-click `.env` → Open with Notepad

**For read-only mode (NO API KEY NEEDED):**
```env
DEMO_MODE=true
```

**For trading mode:**
```env
DEMO_MODE=false

# Uncomment these lines (remove the #):
POLYGON_PRIVATE_KEY=your_64_character_private_key_here
POLYGON_ADDRESS=0xYourAddressHere
```

**Save and close Notepad**

---

### Step 7: Run the Script

Make sure `(polymarket)` is showing in your command prompt, then:

```cmd
python get_realtime_market_data.py
```

**Expected output:**
```
🔥 EXAMPLE 1: Trending Markets with Real-Time Data
================================================================================
📊 REAL-TIME POLYMARKET DATA
================================================================================

🔥 Getting trending markets...
✅ Found 5 markets

📈 MARKET #1: Will Trump win 2024 election?
...
```

---

## 🆘 Troubleshooting (Windows Specific)

### Issue: "python is not recognized"

Try:
```cmd
py -m venv polymarket
py get_realtime_market_data.py
```

Or:
```cmd
python3 -m venv polymarket
python3 get_realtime_market_data.py
```

---

### Issue: "Cannot activate polymarket\Scripts\activate"

If using **PowerShell** instead of Command Prompt:

```powershell
polymarket\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
polymarket\Scripts\Activate.ps1
```

---

### Issue: Can't find .env file

1. Open File Explorer
2. Go to `C:\Users\jmj2z\Projects\polymarket-mcp-server`
3. Click **View** tab at top
4. Check ✅ **"Hidden items"**
5. Check ✅ **"File name extensions"**
6. Now you should see `.env`

---

### Issue: "Module not found" errors

Make sure polymarket is activated:
```cmd
polymarket\Scripts\activate
pip install -e .
```

---

## ✅ Final Verification Checklist

Run these commands to verify everything:

```cmd
# 1. Check you're in the right folder
cd C:\Users\jmj2z\Projects\polymarket-mcp-server

# 2. Check Python is installed
python --version

# 3. Check virtual environment exists
dir polymarket

# 4. Activate it
polymarket\Scripts\activate

# 5. Verify installation
pip list | findstr polymarket-mcp

# 6. Run the script
python get_realtime_market_data.py
```

---

## 📂 Windows File Structure

After setup, your folder should look like:

```
C:\Users\jmj2z\Projects\polymarket-mcp-server\
├── .env                          ← YOUR API KEYS HERE
├── .gitignore
├── get_realtime_market_data.py   ← MAIN SCRIPT TO RUN
├── QUICK_START.md
├── LOCAL_SETUP.md
├── WINDOWS_SETUP.md              ← THIS FILE
├── polymarket\                   ← VIRTUAL ENVIRONMENT
│   ├── Scripts\
│   │   └── activate.bat          ← ACTIVATION SCRIPT
│   └── Lib\
└── src\
    └── polymarket_mcp\
        └── tools\
            ├── market_discovery.py
            ├── market_analysis.py
            └── realtime.py
```

---

## 🎯 Quick Commands Reference (Windows)

```cmd
# Navigate to project
cd C:\Users\jmj2z\Projects\polymarket-mcp-server

# Activate environment
polymarket\Scripts\activate

# Run main script
python get_realtime_market_data.py

# Deactivate when done
deactivate
```

---

## 💡 Pro Tips for Windows

1. **Use Command Prompt (cmd)** not PowerShell for easiest setup
2. **Keep .env file in project root** - same folder as get_realtime_market_data.py
3. **Always activate polymarket** before running Python scripts
4. **Use backslashes `\`** for Windows paths, not forward slashes `/`

---

## 🔑 Where Your API Keys Go

**File:** `C:\Users\jmj2z\Projects\polymarket-mcp-server\.env`

**Lines to edit:**
- Line 7: `DEMO_MODE=true` (for read-only, no API key needed)
- Line 16: `POLYGON_PRIVATE_KEY=...` (for trading)
- Line 20: `POLYGON_ADDRESS=...` (for trading)

**Get your keys from:**
- MetaMask → Settings → Security & Privacy → Export Private Key

---

## ✅ You're Ready!

If all steps completed successfully, you can now:

1. ✅ View real-time market data
2. ✅ Get current prices & probabilities
3. ✅ Search markets
4. ✅ Analyze market opportunities
5. ✅ Monitor market trends

**All without leaving your Windows machine!** 🎉

---

## 🆘 Still Having Issues?

Common Windows-specific issues:

1. **Antivirus blocking Python?** - Add exception for project folder
2. **Firewall blocking API calls?** - Allow Python through Windows Firewall
3. **Path too long error?** - Enable long path support in Windows
4. **Permission denied?** - Run Command Prompt as Administrator

---

**Questions?** Check:
- `QUICK_START.md` - Quick reference
- `LOCAL_SETUP.md` - Detailed guide
- `.env.example` - Configuration template
