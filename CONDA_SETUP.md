# 🐍 Conda Setup Guide - Polymarket MCP Server

**Your Location:** `C:\Users\jmj2z\Projects\polymarket-mcp-server`

---

## 🚀 Quick Start with Conda

### Step 1: Open Anaconda Prompt (or Command Prompt with Conda)

Search for "Anaconda Prompt" in Windows Start menu

### Step 2: Navigate to Project

```bash
cd C:\Users\jmj2z\Projects\polymarket-mcp-server
```

### Step 3: Create Conda Environment

```bash
conda create -n polymarket python=3.11 -y
```

### Step 4: Activate Conda Environment

```bash
conda activate polymarket
```

You should see `(polymarket)` at the start of your prompt!

### Step 5: Install Dependencies

```bash
pip install -e .
```

### Step 6: Run the Script

```bash
python get_realtime_market_data.py
```

**Done!** 🎉

---

## 📋 Full Conda Setup

### Creating the Environment

```bash
# Create environment with Python 3.11
conda create -n polymarket python=3.11 -y

# Or specify Python 3.10
conda create -n polymarket python=3.10 -y

# Activate it
conda activate polymarket
```

### Installing Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install the package
pip install -e .
```

### Verifying Installation

```bash
# Check Python version
python --version

# Check installed packages
conda list | findstr polymarket

# Or
pip list | findstr polymarket
```

---

## 🔧 Daily Workflow with Conda

### First Time Setup (Once)
```bash
cd C:\Users\jmj2z\Projects\polymarket-mcp-server
conda create -n polymarket python=3.11 -y
conda activate polymarket
pip install -e .
```

### Every Time You Use It
```bash
conda activate polymarket
cd C:\Users\jmj2z\Projects\polymarket-mcp-server
python get_realtime_market_data.py
```

### When Done
```bash
conda deactivate
```

---

## 📦 Conda Environment Management

### List All Environments
```bash
conda env list
```

### Remove Environment (if needed)
```bash
conda deactivate
conda env remove -n polymarket
```

### Recreate Environment
```bash
conda create -n polymarket python=3.11 -y
conda activate polymarket
pip install -e .
```

### Update Environment
```bash
conda activate polymarket
pip install --upgrade -e .
```

---

## 🔄 Switching from venv to Conda

If you already created a `venv` or `polymarket` folder with regular Python:

### Step 1: Delete Old Virtual Environment
```bash
# Make sure you're NOT in the environment
deactivate

# Delete the folder
rmdir /s polymarket
# or
rmdir /s venv
```

### Step 2: Create Conda Environment
```bash
conda create -n polymarket python=3.11 -y
conda activate polymarket
pip install -e .
```

---

## 🎯 Conda-Specific Commands

### Check Conda Version
```bash
conda --version
```

### Update Conda
```bash
conda update conda
```

### Install Additional Packages (if needed)
```bash
conda activate polymarket
conda install numpy pandas -y
```

### Export Environment (for sharing)
```bash
conda activate polymarket
conda env export > environment.yml
```

### Create from environment.yml
```bash
conda env create -f environment.yml
```

---

## 🆘 Conda Troubleshooting

### Error: "conda is not recognized"

**Option 1:** Use Anaconda Prompt instead of regular Command Prompt

**Option 2:** Add Conda to PATH
1. Find your Anaconda/Miniconda installation (usually `C:\Users\jmj2z\Anaconda3` or `C:\Users\jmj2z\Miniconda3`)
2. Add these to your PATH:
   - `C:\Users\jmj2z\Anaconda3`
   - `C:\Users\jmj2z\Anaconda3\Scripts`
   - `C:\Users\jmj2z\Anaconda3\Library\bin`

### Error: Environment activation issues

```bash
# Try initializing conda for your shell
conda init cmd.exe

# Restart Command Prompt, then:
conda activate polymarket
```

### Error: Package conflicts

```bash
# Create fresh environment
conda deactivate
conda env remove -n polymarket
conda create -n polymarket python=3.11 -y
conda activate polymarket
pip install -e .
```

---

## 🔍 Verify Conda Setup

Run these commands to verify:

```bash
# 1. Check conda is installed
conda --version

# 2. List environments (should show 'polymarket')
conda env list

# 3. Activate environment
conda activate polymarket

# 4. Check Python version
python --version

# 5. Check packages
pip list

# 6. Run the script
python get_realtime_market_data.py
```

---

## 💡 Conda vs venv

| Feature | Conda | venv |
|---------|-------|------|
| Python version control | ✅ Yes | ❌ No |
| Package management | Both conda & pip | pip only |
| Non-Python packages | ✅ Yes | ❌ No |
| Environment location | Centralized | Project folder |
| Speed | Slower | Faster |
| Disk space | More | Less |

**For this project:** Both work fine! Use whichever you prefer.

---

## 📂 File Structure with Conda

```
C:\Users\jmj2z\Projects\polymarket-mcp-server\
├── .env                          ← API keys here
├── get_realtime_market_data.py   ← Main script
├── CONDA_SETUP.md                ← This file
├── WINDOWS_SETUP.md              ← venv guide
├── src\
│   └── polymarket_mcp\
│       └── tools\
└── (no polymarket/ folder!)      ← Conda envs stored elsewhere
```

**Note:** Conda environments are stored in:
- Windows: `C:\Users\jmj2z\Anaconda3\envs\polymarket\`
- Not in your project folder

---

## 🎯 Quick Reference Card

### Create Environment
```bash
conda create -n polymarket python=3.11 -y
```

### Activate
```bash
conda activate polymarket
```

### Install
```bash
pip install -e .
```

### Run
```bash
python get_realtime_market_data.py
```

### Deactivate
```bash
conda deactivate
```

### Remove
```bash
conda env remove -n polymarket
```

---

## ✅ Conda Setup Checklist

- [ ] Anaconda or Miniconda installed
- [ ] Opened Anaconda Prompt
- [ ] Navigated to `C:\Users\jmj2z\Projects\polymarket-mcp-server`
- [ ] Created conda env: `conda create -n polymarket python=3.11 -y`
- [ ] Activated: `conda activate polymarket`
- [ ] Saw `(polymarket)` in prompt
- [ ] Installed: `pip install -e .`
- [ ] Ran: `python get_realtime_market_data.py`
- [ ] Saw real market data

---

## 🔗 Conda Resources

- **Conda Cheat Sheet:** https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html
- **Managing Environments:** https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
- **Download Anaconda:** https://www.anaconda.com/download
- **Download Miniconda:** https://docs.conda.io/en/latest/miniconda.html

---

**Ready to use Conda?**

```bash
conda create -n polymarket python=3.11 -y
conda activate polymarket
pip install -e .
python get_realtime_market_data.py
```

**Let's go!** 🐍🚀
