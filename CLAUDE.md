# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## LocalMind Collective - Oxford AI Summit 2025 Demo

A multi-agent AI research system running entirely on local hardware, designed for live presentations emphasizing data sovereignty and eliminating cloud dependencies.

## Commands for Development

### Initial Setup
```bash
# Install dependencies
pip install -r demo/requirements.txt

# Download required models (~18GB, one-time setup)
./models/pull_models.sh

# Configure environment
cp .env.example .env
# Edit .env for optional API keys (BRAVE_API_KEY for web search)
```

### Running the System
```bash
# Launch demo server (creates venv, checks models, starts FastAPI)
cd demo && ./launch.sh

# Access dashboard at http://localhost:8000
```

### Testing
```bash
# Test enhanced orchestrator initialization
cd demo && python test_enhanced_quick.py

# Run pre-presentation test suite
cd demo && python test_slides_display.py
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

## Architecture Overview

### Multi-Agent System
The demo orchestrates 5 specialized agents that collaborate in real-time:

1. **Principal Synthesizer** (deepseek-r1:8b) - Deep reasoning and orchestration
2. **Domain Specialist** (qwen3:8b) - Expert domain analysis  
3. **Web Harvester** (qwen3:4b) - Quick web research
4. **Fact Validator** (phi4-mini) - Claim verification
5. **Quality Auditor** (phi4-mini) - Output assessment

### Enhanced Production Features

The enhanced orchestrator (`demo/agents/orchestrator_enhanced.py`) includes:
- **Structured Prompting**: XML-based templates with validation (`demo/agents/core/prompting.py`)
- **Resilient Execution**: Automatic retries, fallbacks, circuit breakers (`demo/agents/core/resilience.py`)
- **Memory System**: SQLite-based learning across sessions (`demo/agents/core/memory.py`)
- **Agent Communication**: Structured handoffs and context sharing (`demo/agents/core/communication.py`)
- **Dynamic Optimization**: Adaptive temperature and timeout adjustments (`demo/agents/core/dynamic.py`)

### Key Components

- **`demo/app.py`**: FastAPI server with WebSocket support for real-time streaming
- **`demo/agents/base.py`**: Enhanced base agent class with production features
- **`demo/agents/core/`**: Framework components for production-ready agent systems
- **`demo/static/`**: Web UI with real-time visualization
- **`demo/utils/system_monitor.py`**: VRAM and performance monitoring

### Technical Stack
- FastAPI with WebSocket support for real-time agent streaming
- Ollama for local model execution
- Optional Brave Search API for web capabilities
- Quantized models optimized for consumer hardware (RTX 3080/4070+, Apple Silicon)
- SQLite for persistent memory storage

## Development Guidelines

1. **Optimize for Live Demos**: Response times should be 30s-2min for audience engagement
2. **Local-First**: All processing must happen locally, no cloud dependencies
3. **Visual Feedback**: Ensure real-time progress visualization for presentations
4. **Hardware Awareness**: Monitor and display VRAM usage for transparency
5. **Resilient Design**: Use the production features (retries, fallbacks) for reliability

## Pre-configured Demo Scenarios

The system includes scenarios optimized for presentations:
- Benefits of Local AI (2min)
- AI Agent Orchestration (2min)
- AI Safety & Alignment 2025 (2min)
- Quantum Computing Breakthroughs (90s)
- AI for Climate Change (2min)
- Edge AI & IoT Trends (90s)

## Environment Configuration

Optional environment variables in `.env`:
```bash
BRAVE_API_KEY=your_api_key          # For real web search
ANTHROPIC_API_KEY=your_key          # For PII detection demo
GITHUB_TOKEN=your_token             # For GitHub integration
OLLAMA_HOST=http://localhost:11434  # Ollama service endpoint
DEBUG=true                          # Enable debug logging
LOG_LEVEL=debug                     # Logging verbosity
```

## Important Notes

- This is a focused demo project, not the full multi-agent research system
- Models are quantized for efficiency on consumer hardware  
- Web search is optional and can be simulated for offline demos
- The UI is designed for projection and live audience viewing
- No traditional test framework - custom test scripts for demo validation
- All processing happens locally for complete data sovereignty