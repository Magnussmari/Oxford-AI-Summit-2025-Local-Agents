"""
LocalMind Collective - Oxford AI Summit 2025 Presentation Demo
Live demonstration matching slide content with real-time agent execution
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import psutil
import platform
from datetime import datetime
from pathlib import Path
import sys
import os
from loguru import logger
import subprocess
import time
from typing import Dict, Any
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from root .env file
root_dir = Path(__file__).parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

from agents.orchestrator_enhanced import ProductionOrchestrator
from utils.system_monitor import get_system_thermal_info

app = FastAPI(title="Magnus Smari | Oxford AI Summit 2025")

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Global state
logger.info("Using enhanced production orchestrator with all improvements")
orchestrator = ProductionOrchestrator(use_enhanced=True)
connections = set()
is_processing = False

# Demo scenarios optimized for enhanced orchestrator
DEMO_SCENARIOS = [
    {
        "id": "local_ai_benefits",
        "title": "Benefits of Local AI ",
        "description": "Comprehensive analysis with fact-checking (2 minutes)",
        "query": "Analyze the benefits and challenges of running AI systems locally versus cloud-based solutions. Research current industry trends, privacy regulations like GDPR, cost comparisons, and real-world case studies. Include specific examples of companies successfully using local AI.",
        "mode": "expert",
        "expected_time": "~2min",
        "agents": ["Principal Synthesizer", "Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"],
        "highlights": ["Comprehensive analysis", "Fact validation", "Quality assessment", "Data sovereignty focus"]
    },
    {
        "id": "agent_orchestration",
        "title": "AI Agent Orchestration Best Practices",
        "description": "Technical deep-dive with validation (2 minutes)",
        "query": "Research the latest best practices for orchestrating multiple AI agents in production systems. Find information about frameworks like AutoGen, LangGraph, and CrewAI. Include specific implementation patterns, error handling strategies, and performance benchmarks from recent studies.",
        "mode": "expert",
        "expected_time": "~2min",
        "agents": ["Principal Synthesizer", "Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"],
        "highlights": ["Production patterns", "Technical validation", "Resilience focus", "Expert analysis"]
    },
    {
        "id": "ai_safety_2025",
        "title": "AI Safety & Alignment in 2025",
        "description": "Current state analysis with web research (2 minutes)",
        "query": "What are the latest developments in AI safety and alignment as of 2025? Research recent papers, industry initiatives, and regulatory frameworks. Include specific examples of safety measures being implemented by leading AI labs and any recent incidents or breakthroughs.",
        "mode": "expert",
        "expected_time": "~2min",
        "agents": ["Principal Synthesizer", "Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"],
        "highlights": ["Current research", "Web exploration", "Fact checking", "Quality review"]
    },
    {
        "id": "quantum_breakthroughs",
        "title": "Recent Quantum Computing Breakthroughs",
        "description": "Latest developments with verification (90 seconds)",
        "query": "What are the most significant quantum computing breakthroughs in the past 12 months? Research specific achievements by companies like IBM, Google, and IonQ. Include technical details about qubit counts, error rates, and practical applications being developed.",
        "mode": "auto",
        "expected_time": "~90s",
        "agents": ["Principal Synthesizer", "Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"],
        "highlights": ["Recent news", "Technical validation", "Industry updates", "Fact verification"]
    },
    {
        "id": "climate_ai_solutions",
        "title": "AI for Climate Change Solutions",
        "description": "Environmental tech analysis (2 minutes)",
        "query": "How is AI being used to combat climate change in 2025? Research specific projects, companies, and technologies. Include examples of AI applications in renewable energy optimization, carbon capture, and climate modeling. Find recent success stories and measurable impacts.",
        "mode": "expert",
        "expected_time": "~2min",
        "agents": ["Principal Synthesizer", "Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"],
        "highlights": ["Real applications", "Impact metrics", "Web research", "Fact validation"]
    },
    {
        "id": "edge_ai_trends",
        "title": "Edge AI & IoT Trends 2025",
        "description": "Technology landscape analysis (90 seconds)",
        "query": "What are the latest trends in edge AI and IoT for 2025? Research new hardware like neuromorphic chips, software frameworks, and real-world deployments. Include specific examples of edge AI applications in smartphones, autonomous vehicles, and smart cities.",
        "mode": "auto",
        "expected_time": "~90s",
        "agents": ["Principal Synthesizer", "Domain Specialist", "Web Harvester", "Fact Validator", "Quality Auditor"],
        "highlights": ["Hardware advances", "Software trends", "Market analysis", "Technical validation"]
    }
]

# Model information for display
MODEL_INFO = {
    "deepseek-r1:8b": {"size": "5.2GB", "context": "16K", "role": "Principal Synthesizer"},
    "qwen3:8b": {"size": "5.2GB", "context": "32K", "role": "Domain Specialist"},
    "qwen3:4b": {"size": "2.6GB", "context": "32K", "role": "Web Harvester"},
    "phi4-mini": {"size": "2.5GB", "context": "128K", "role": "Fact Validator & Quality Auditor"}
}

class PresentationDemo:
    """Manages the live presentation demo."""
    
    def __init__(self):
        self.start_time = None
        self.agent_metrics = {}
        self.vram_baseline = None
        
    async def research_with_streaming(self, query: str, mode: str, websocket: WebSocket):
        """Execute research with real-time streaming updates."""
        
        self.start_time = time.time()
        self.agent_metrics = {}
        
        # Send initialization
        await websocket.send_json({
            "type": "init",
            "query": query,
            "mode": mode,
            "timestamp": datetime.now().isoformat()
        })
        
        # Callback for streaming updates
        async def stream_callback(update):
            update["elapsed"] = round(time.time() - self.start_time, 1)
            try:
                await websocket.send_json(update)
            except Exception as e:
                logger.warning(f"Could not send update - WebSocket may be closed: {e}")
        
        # Start performance monitoring task
        performance_task = asyncio.create_task(self._send_performance_updates(websocket))
        
        try:
            # Get baseline VRAM
            self.vram_baseline = self._get_vram_usage()
            
            # Execute research with streaming
            result = await orchestrator.research(query, mode, stream_callback)
            
            # Add execution metrics
            result["metrics"] = {
                "total_time": round(time.time() - self.start_time, 1),
                "vram_peak": self._get_vram_usage(),
                "vram_baseline": self.vram_baseline,
                "agent_count": len(result["agents_used"]),
                "web_search": result.get("web_search_used", False)
            }
            
            # Send completion
            await websocket.send_json({
                "type": "complete",
                "result": result
            })
            
            # Cancel performance monitoring
            performance_task.cancel()
            
        except Exception as e:
            logger.error(f"Demo error: {e}")
            # Cancel performance monitoring
            performance_task.cancel()
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            except Exception:
                logger.warning("Could not send error message - WebSocket may be closed")
    
    def _get_vram_usage(self) -> Dict[str, Any]:
        """Get current VRAM usage."""
        try:
            # Try nvidia-smi for NVIDIA GPUs
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                used, total = map(float, result.stdout.strip().split(', '))
                return {
                    "used_gb": round(used / 1024, 1),
                    "total_gb": round(total / 1024, 1),
                    "percent": round((used / total) * 100, 1)
                }
        except:
            pass
        
        # Fallback to system memory
        mem = psutil.virtual_memory()
        return {
            "used_gb": round((mem.total - mem.available) / (1024**3), 1),
            "total_gb": round(mem.total / (1024**3), 1),
            "percent": mem.percent
        }
    
    async def _send_performance_updates(self, websocket):
        """Send periodic performance updates to the client."""
        try:
            while True:
                await asyncio.sleep(1)  # Update every second
                vram_info = self._get_vram_usage()
                
                # Send performance update
                await websocket.send_json({
                    "type": "performance",
                    "vram": vram_info,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            logger.debug(f"Performance monitoring stopped: {e}")

# Create demo instance
demo = PresentationDemo()

@app.get("/")
async def read_root():
    """Serve the main demo page."""
    return FileResponse(static_dir / "index.html")

@app.get("/api/scenarios")
async def get_scenarios():
    """Get demo scenarios."""
    return DEMO_SCENARIOS

@app.get("/api/models")
async def get_models():
    """Get model information."""
    # Check which models are actually available
    available = []
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for model_id, info in MODEL_INFO.items():
                if any(model_id in line for line in lines):
                    available.append({
                        "id": model_id,
                        **info,
                        "available": True
                    })
                else:
                    available.append({
                        "id": model_id,
                        **info,
                        "available": False
                    })
    except:
        for model_id, info in MODEL_INFO.items():
            available.append({
                "id": model_id,
                **info,
                "available": False
            })
    
    return available

@app.get("/api/system")
async def get_system_info():
    """Get system information for display."""
    # GPU info
    gpu_info = "Not detected"
    vram_info = demo._get_vram_usage()
    
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            gpu_info = result.stdout.strip()
    except:
        if platform.system() == "Darwin":
            gpu_info = "Apple Silicon"
    
    # Get thermal info
    thermal_info = get_system_thermal_info()
    
    # Get enhanced features status
    enhanced_features = {
        "enabled": True,
        "features": [
            "Structured prompting",
            "Chain-of-Thought reasoning",
            "Resilient execution",
            "Memory system",
            "Agent communication",
            "Adaptive temperature",
            "Prompt optimization"
        ]
    }
    # Get system health if available
    if hasattr(orchestrator, 'get_system_health'):
        enhanced_features["health"] = orchestrator.get_system_health()

    return {
        "platform": f"{platform.system()} {platform.release()}",
        "processor": platform.processor() or platform.machine(),
        "gpu": gpu_info,
        "vram": vram_info,
        "cpu_cores": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "brave_api": "Active" if os.getenv("BRAVE_API_KEY") else "Not configured",
        "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "enhanced_mode": enhanced_features,
        "cpu_temp": thermal_info.get("cpu_temp"),
        "fans": thermal_info.get("fans"),
        "thermal_available": thermal_info.get("available", False),
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time demo updates."""
    global is_processing
    
    await websocket.accept()
    connections.add(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "research":
                if not is_processing:
                    is_processing = True
                    await demo.research_with_streaming(
                        data["query"],
                        data.get("mode", "auto"),
                        websocket
                    )
                    is_processing = False
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Already processing a query"
                    })
            
            elif data["type"] == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in connections:
            connections.remove(websocket)
        is_processing = False

if __name__ == "__main__":
    import uvicorn
    
    # Only show startup message if not disabled by launch script
    if not os.getenv("LOCALMIND_NO_STARTUP_MSG"):
        print("\n" + "="*60)
        print("🚀 Magnus Smari - Local AI Agents | Oxford AI Summit 2025")
        print("="*60)
        print("\n📍 Starting server at http://localhost:8000")
        print("\n🎯 Demo Features:")
        print("  • Live multi-agent execution with smaller models")
        print("  • Real-time progress visualization")
        print("  • VRAM and performance monitoring")
        print("  • Scenarios matching presentation slides")
        print("  • Optional web search integration")
        print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)