# Local Agentic System - Oxford AI Summit 2025

> **Enterprise-Ready Multi-Agent AI System (100% Local Execution)**

## Overview

This repository contains a modular, production-grade multi-agent AI framework that runs entirely on local hardware. It orchestrates multiple specialized agents for advanced reasoning, research, validation, and quality assurance—no cloud required.

## Features
- 100% local execution (no external dependencies)
- Multi-agent orchestration with streaming responses
- Modular, extensible agent framework
- Real-time web interface
- Runs on consumer GPUs or Apple Silicon

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed
- 18GB+ VRAM recommended (or Apple Silicon with 32GB+ memory)

### Installation
```bash
# Clone the repository
git clone https://github.com/Magnussmari/Oxford-ai-summit-2025-Local-Agents.git
cd Oxford-ai-summit-2025-Local-Agents

# Install dependencies
pip install -r demo/requirements.txt

# Download required models
./models/pull_models.sh

# Launch the demo
cd demo && ./launch.sh
```
Visit http://localhost:8000 to use the system.

## Agent Team

| Agent                | Model           | Purpose                    |
|----------------------|-----------------|----------------------------|
| Principal Synthesizer| deepseek-r1:8b  | Reasoning & orchestration  |
| Domain Specialist    | qwen3:8b        | Expert domain analysis     |
| Web Harvester        | qwen3:4b        | Web research               |
| Fact Validator       | phi4-mini       | Claim verification         |
| Quality Auditor      | phi4-mini       | Output assessment          |

## Repository Structure
```
demo/
  app.py           # FastAPI server
  agents/          # Agent implementations
  static/          # Web UI (HTML/CSS/JS)
  utils/           # Monitoring utilities
  launch.sh        # Demo launcher
models/
  pull_models.sh   # Download models
```

## Customization Guide

### Adding a New Agent
1. Create your agent in `demo/agents/your_agent.py`:
```python
from .base import PresentationAgent
class YourAgent(PresentationAgent):
    def __init__(self):
        super().__init__(name="Your Agent", model="model_name:tag", role="specialist", temperature=0.7)
    async def process(self, query: str, context: dict, stream_callback=None) -> str:
        prompt = f"Your prompt: {query}"
        return await self.run(prompt, stream_callback)
```
2. Register it in `agents/orchestrator_enhanced.py`.

### Modifying Agent Behavior
- Change models: edit agent `__init__`
- Adjust prompts: modify agent prompt templates
- Orchestration: update `orchestrator_enhanced.py`
- UI: edit files in `static/`

## FAQ

**Q: Can I use different models?**  
A: Yes, any Ollama-compatible model. Update the agent class.

**Q: How do I enable web search?**  
A: Add a Brave Search API key to `.env` as `BRAVE_API_KEY`.

**Q: What are the hardware requirements?**  
A: 18GB VRAM recommended, but smaller models can run on 8-12GB GPUs.

## Troubleshooting
- **Models not found**: Run `./models/pull_models.sh`
- **Out of memory**: Use fewer agents or smaller models
- **WebSocket errors**: Ensure port 8000 is open
- **Import errors**: Run commands from the project root

## License

MIT License. See [LICENSE](LICENSE) for details.
