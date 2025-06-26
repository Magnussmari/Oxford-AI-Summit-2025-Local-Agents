# LocalMind Collective - Oxford AI Summit 2025

> **Building Enterprise Multi-Agent AI Systems Locally**

** | 📊 **[View Slides](presentation/slides.md)** | 🚀 **[Try the Demo](#quick-start)**

## 🌟 Overview

Transform single AI models into orchestrated multi-agent systems running entirely on local hardware. This repository contains the presentation and live demo from Oxford AI Summit 2025.

### Key Features

- **100% Local Execution** - No cloud dependencies, complete data sovereignty
- **Multi-Agent Orchestration** - 5 specialized agents working together
- **Consumer Hardware** - Runs on RTX 3080/4070+ or Apple Silicon
- **Real-time Demo** - Watch agents collaborate with streaming responses

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) installed
- 18GB+ VRAM recommended (or Apple Silicon with 32GB+ unified memory)

### Installation

```bash
# Clone the repository
git clone https://github.com/Magnussmari/Oxford-ai-summit-2025-Local-Agents.git
cd Oxford-ai-summit-2025-Local-Agents

# Install Python dependencies
pip install -r demo/requirements.txt

# Pull required models (one-time setup, ~18GB total)
./models/pull_models.sh

# Launch the demo
cd demo && ./launch.sh
```

Visit http://localhost:8000 to see the agents in action!

## 🤖 The Agent Team

| Agent | Model | Purpose | VRAM |
|-------|-------|---------|------|
| **Principal Synthesizer** | deepseek-r1:8b | Deep reasoning & orchestration | 5.2GB |
| **Domain Specialist** | qwen3:8b | Expert domain analysis | 5.2GB |
| **Web Harvester** | qwen3:4b | Quick web research | 2.6GB |
| **Fact Validator** | phi4-mini | Claim verification | 2.5GB |
| **Quality Auditor** | phi4-mini | Output assessment | 2.5GB |

## 📁 Repository Structure

```
├── presentation/          # Presentation materials
│   ├── slides.md         # Marp presentation slides
│   └── images/           # Screenshots and visuals
├── demo/                 # Live demo application
│   ├── app.py           # Flask server
│   ├── agents_presentation.py  # Agent implementations
│   ├── launch.sh        # Demo launcher
│   └── static/          # Web interface
└── models/              # Model setup scripts
    └── pull_models.sh   # Download all required models
```

## 🎯 Demo Scenarios

1. **Simple Query** (30s): "What is quantum computing?"
2. **Complex Analysis** (2min): "Analyze mRNA vaccine mechanisms..."
3. **Current Events** (1min): "Latest AI safety developments"

## 🛠️ Troubleshooting

- **Models not found**: Run `./models/pull_models.sh` to download all models
- **Out of memory**: Try running fewer agents or use smaller model variants
- **Slow performance**: Ensure Ollama is using GPU acceleration

## 👨‍💻 About

**Presenter**: Magnús Smári Smárason  
**Event**: Oxford AI Summit 2025  
**Location**: Oxford, United Kingdom  

Built with ❤️ in Iceland 🇮🇸

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🔗 Links

- **Email**: magnus@smarason.is
- **Web**: www.smarason.is
- **Main Project**: [github.com/Magnussmari/multi-agent-research-system](https://github.com/Magnussmari/multi-agent-research-system)
