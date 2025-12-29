#!/bin/bash
# Quick run script for Polymarket MCP Real-Time Data

echo "🚀 Polymarket MCP - Real-Time Data"
echo "=================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -e . -q
    echo "✅ Virtual environment created!"
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi

echo ""
echo "📊 Running real-time market data script..."
echo ""

python get_realtime_market_data.py

echo ""
echo "✅ Done!"
