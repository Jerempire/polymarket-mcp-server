#!/bin/bash
# Quick run script for Polymarket MCP Real-Time Data

echo "🚀 Polymarket MCP - Real-Time Data"
echo "=================================="
echo ""

# Check if polymarket env exists
if [ ! -d "polymarket" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv polymarket
    source polymarket/bin/activate
    pip install --upgrade pip -q
    pip install -e . -q
    echo "✅ Virtual environment created!"
else
    echo "✅ Virtual environment found"
    source polymarket/bin/activate
fi

echo ""
echo "📊 Running real-time market data script..."
echo ""

python get_realtime_market_data.py

echo ""
echo "✅ Done!"
