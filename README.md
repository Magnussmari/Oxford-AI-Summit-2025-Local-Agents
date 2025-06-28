# LocalMind Collective - Oxford AI Summit 2025

> **Building Enterprise Multi-Agent AI Systems Locally**

📊 **[View Slides](presentation/slides.md)** | 🚀 **[Try the Demo](#quick-start)**

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

1. **Benefits of Local AI** (2min): Comprehensive analysis with web research and fact validation
2. **AI Agent Orchestration** (2min): Latest frameworks like AutoGen, LangGraph, and CrewAI
3. **AI Safety & Alignment 2025** (2min): Current developments with real-time web search
4. **Quantum Computing Breakthroughs** (90s): Recent achievements by IBM, Google, and IonQ
5. **AI for Climate Change** (2min): Specific projects and measurable impacts
6. **Edge AI & IoT Trends** (90s): Neuromorphic chips and smart city applications

*All scenarios include **websites explored** tracking for transparency*

## 🚀 Production Features

The system includes enterprise-grade features for production deployment:

### Core Features
- **Structured Prompting**: XML-based prompt templates with validation
- **Chain-of-Thought Reasoning**: Deep analytical thinking for complex queries
- **Resilient Execution**: Automatic retries, fallbacks, and circuit breakers
- **Memory System**: SQLite-based learning from past interactions
- **Agent Communication**: Structured handoffs and context sharing
- **Web Search Integration**: Real-time research with source tracking
- **Adaptive Temperature**: Dynamic temperature adjustment based on context
- **Prompt Optimization**: Token reduction and caching for efficiency

## 🛠️ My Current AI Development Toolkit

**Primary Development Environment:**
- **VS Code** with GitHub Copilot - Primary coding with AI assistance
- **Claude Code (Max plan)** - Advanced code analysis and refactoring

**Secondary Tools:**
- **Cursor Pro** - AI-first code editor for complex projects

**Daily AI Drivers:**
- **Claude Desktop** - Research, planning, and problem-solving
- **ChatGPT** - Specialized tasks and alternative perspectives
- **Gemini** - Multimodal analysis and creative workflows

**Philosophy**: *AI-assisted development isn't just about coding - it's about thinking, planning, and iterating faster*

### Testing Production Features
```bash
# Run the enhanced orchestrator test suite
cd demo && python test_enhanced_quick.py
```

## 🛠️ Troubleshooting

- **Models not found**: Run `./models/pull_models.sh` to download all models
- **Out of memory**: Try running fewer agents or use smaller model variants
- **Slow performance**: Ensure Ollama is using GPU acceleration

## 👨‍💻 About

**Presenter**: Magnús Smári Smárason  
**Event**: Oxford AI Summit 2025  
**Location**: Oxford, United Kingdom  

**Portfolio**: [View My AI Projects](Projects_portfolio/) - Arctic species tracking, fire protection systems, and university AI infrastructure

Built with ❤️ in Iceland 🇮🇸 using AI-assisted development

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🔗 Links

- **Email**: magnus@smarason.is
- **Web**: www.smarason.is
- **Main Project**: [github.com/Magnussmari/multi-agent-research-system](https://github.com/Magnussmari/multi-agent-research-system)