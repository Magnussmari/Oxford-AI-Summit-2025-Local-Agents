#!/bin/bash

# LocalMind Collective - Oxford AI Summit 2025 Demo Launcher

echo "=================================================="
echo "🚀 LocalMind Collective - Oxford AI Summit 2025"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "../../venv" ]; then
    echo "Creating virtual environment..."
    cd ../..
    uv venv
    cd demo_frontend/presentation_demo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source ../../venv/bin/activate

# Install requirements if needed
echo "Checking dependencies..."
pip install -q fastapi uvicorn websockets httpx psutil loguru aiohttp

# Check for required models
echo ""
echo "Checking required models..."
echo "--------------------------"

REQUIRED_MODELS=("deepseek-r1:8b" "qwen3:8b" "qwen3:4b" "phi4-mini")
MISSING_MODELS=()

for model in "${REQUIRED_MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "✓ $model installed"
    else
        echo "✗ $model missing"
        MISSING_MODELS+=("$model")
    fi
done

if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Missing models detected!"
    echo "Install with: ollama pull <model-name>"
    echo ""
fi

# Check for Brave API key
if [ -z "$BRAVE_API_KEY" ]; then
    echo ""
    echo "⚠️  No BRAVE_API_KEY found - web search will be simulated"
    echo "Set with: export BRAVE_API_KEY='your-key'"
else
    echo ""
    echo "✓ Brave Search API configured"
fi

echo ""
echo "=================================================="
echo "Starting LocalMind Collective Demo..."
echo "=================================================="
echo ""
echo "📍 Open http://localhost:8000 in your browser"
echo ""
echo "Demo Features:"
echo "  • Live multi-agent orchestration"
echo "  • Real-time progress visualization"
echo "  • VRAM and performance monitoring"
echo "  • Pre-configured demo scenarios"
echo ""
echo "Press Ctrl+C to stop"
echo "=================================================="
echo ""

# Launch the app
python app.py