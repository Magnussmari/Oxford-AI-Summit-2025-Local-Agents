# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## LocalMind Collective - Oxford AI Summit 2025 Demo

This is a demonstration project showcasing multi-agent AI systems running entirely on local hardware. It's designed for live presentations and emphasizes data sovereignty by eliminating cloud dependencies.

## Commands for Development

### Setup and Launch
```bash
# Install dependencies (from demo directory)
pip install -r requirements.txt

# Download required models (~18GB, one-time setup)
./models/pull_models.sh

# Launch the demo server
cd demo && ./launch.sh
```

### Model Management
```bash
# Check installed models
ollama list

# Pull individual models if needed
ollama pull deepseek-r1:8b
ollama pull qwen3:8b
ollama pull qwen3:4b
ollama pull phi4-mini
```

### Environment Variables
```bash
# Optional: Enable real web search (otherwise simulated)
export BRAVE_API_KEY='your-api-key'
```

## Architecture Overview

### Multi-Agent System
The demo orchestrates 5 specialized agents that collaborate in real-time:

1. **Principal Synthesizer** (deepseek-r1:8b) - Deep reasoning and orchestration
2. **Domain Specialist** (qwen3:8b) - Expert domain analysis
3. **Web Harvester** (qwen3:4b) - Quick web research
4. **Fact Validator** (phi4-mini) - Claim verification
5. **Quality Auditor** (phi4-mini) - Output assessment

### Key Components

- **`demo/app.py`**: FastAPI server with WebSocket support for real-time streaming
- **`demo/agents_presentation.py`**: Agent implementations optimized for live demos
- **`demo/static/`**: Web UI with real-time visualization
- **`demo/utils/system_monitor.py`**: VRAM and performance monitoring

### Technical Stack
- FastAPI with WebSocket support for real-time agent streaming
- Ollama for local model execution
- Optional Brave Search API for web capabilities
- Quantized models optimized for consumer hardware (RTX 3080/4070+ or Apple Silicon)

## Development Guidelines

1. **Optimize for Live Demos**: Response times should be 30s-2min for audience engagement
2. **Local-First**: All processing must happen locally, no cloud dependencies
3. **Visual Feedback**: Ensure real-time progress visualization for presentations
4. **Hardware Awareness**: Monitor and display VRAM usage for transparency

## Demo Scenarios

The system includes pre-configured scenarios optimized for presentations:
- Simple queries (~30s): Basic concept explanations
- Complex analysis (~2min): Multi-faceted research questions
- Current events (~1min): Recent developments requiring web search

## Important Notes

- This is a focused demo project, not the full multi-agent research system
- Models are quantized for efficiency on consumer hardware
- Web search is optional and can be simulated for offline demos
- The UI is designed for projection and live audience viewing