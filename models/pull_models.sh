#!/bin/bash
# Pull all required models for the Oxford AI Summit 2025 demo

echo "🤖 LocalMind Collective - Model Setup"
echo "====================================="
echo ""
echo "This will download ~18GB of models. Make sure you have enough disk space."
echo ""

# Check if ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install it from https://ollama.ai"
    exit 1
fi

echo "📥 Pulling required models..."
echo ""

# Array of models to pull
models=(
    "deepseek-r1:8b"
    "qwen3:8b"
    "qwen3:4b"
    "phi4-mini"
)

# Pull each model
for model in "${models[@]}"; do
    echo "⏳ Pulling $model..."
    if ollama pull "$model"; then
        echo "✅ $model downloaded successfully"
    else
        echo "❌ Failed to pull $model"
        exit 1
    fi
    echo ""
done

echo "🎉 All models downloaded successfully!"
echo ""
echo "You can now run the demo with:"
echo "  cd ../demo && ./launch.sh"