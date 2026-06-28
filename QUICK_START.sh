#!/bin/bash

echo "🧠 CertMind Quick Start Script"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if UI is built
if [ ! -d "ui/dist" ]; then
    echo "🏗️  Building React UI..."
    cd ui
    npm install
    npm run build
    cd ..
else
    echo "✅ UI already built (ui/dist exists)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Choose your demo:"
echo ""
echo "1️⃣  Terminal Demo (simple):"
echo "   python scripts/demo.py"
echo ""
echo "2️⃣  Full Terminal Demo (all 4 scenarios):"
echo "   python scripts/demo_full.py"
echo ""
echo "3️⃣  Web UI Demo:"
echo "   python scripts/ui_server.py"
echo "   Then open: http://localhost:8080"
echo ""
