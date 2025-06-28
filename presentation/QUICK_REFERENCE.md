# Oxford AI Summit 2025 - Quick Reference Card

## 🚀 Launch Sequence
```bash
cd oxford-ai-summit-2025-clean/demo
./launch.sh
# Browser: http://localhost:8000
```

## 🎯 Demo Queries (Copy & Paste)

### 30-Second Demos
```
What are the key differences between edge AI and cloud AI?
```

### 90-Second Demos
```
Research current quantum computing breakthroughs from IBM, Google and IonQ
```

### 2-Minute Full Demos
```
Analyze the benefits and challenges of running AI models locally versus cloud-based solutions, including recent industry trends and specific case studies
```

## 🔥 Key Stats to Mention
- **18GB VRAM** total for all agents
- **2 developers** built BORG system
- **$0** ongoing API costs
- **100%** data sovereignty
- **30,000 feet** - where you worked on slides

## 💬 Power Phrases
- "This is running entirely on local hardware"
- "No cloud dependencies, complete data sovereignty"
- "Built by just 2 developers serving a whole university"
- "Your data never leaves your infrastructure"
- "Consumer GPU, enterprise capabilities"

## 🛠️ Tech Stack (for questions)
- **Models**: DeepSeek-R1, Qwen3, Phi-4
- **Backend**: FastAPI + WebSockets
- **Inference**: Ollama
- **Frontend**: Vanilla JS (intentionally simple)
- **Memory**: SQLite for persistence

## 🆘 Troubleshooting Commands
```bash
# Check models
ollama list

# Restart Ollama
sudo systemctl restart ollama

# Check GPU
nvidia-smi

# Emergency kill
pkill -f "python.*app.py"
```

## 📊 Agent Overview
| Agent | Purpose | Model | VRAM |
|-------|---------|-------|------|
| Principal | Orchestration | deepseek-r1:8b | 5.2GB |
| Domain | Analysis | qwen3:8b | 5.2GB |
| Web | Research | qwen3:4b | 2.6GB |
| Fact | Validation | phi4-mini | 2.5GB |
| Quality | Assessment | phi4-mini | 2.5GB |

## 🎪 Audience Engagement
- "What would you like to research?"
- "Notice how the agents collaborate"
- "Watch the token counter - all local!"
- "See the websites being validated?"
- "This could run on your laptop"

## 📱 Contact for Sharing
```
GitHub: github.com/Magnussmari
Email: magnus@smarason.is
Project: /Oxford-ai-summit-2025-Local-Agents
```

## 🎯 One-Liners for Networking
- "I build AI systems that run entirely on your hardware"
- "Enterprise AI without the cloud dependency"
- "Multi-agent systems for data sovereignty"
- "Like having GPT-4 in your server room"

## ⏱️ Time Markers
- 0:00 - Hook & Introduction
- 2:30 - Project showcase
- 10:00 - Platform introduction
- 19:00 - LIVE DEMO
- 25:00 - Wrap up & takeaways
- 29:00 - Questions

## 🔑 Remember
**You built this. It works. It's revolutionary. Share your passion!**