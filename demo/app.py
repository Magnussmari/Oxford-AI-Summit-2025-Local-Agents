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

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agents_presentation import PresentationOrchestrator
from utils.system_monitor import get_system_thermal_info

app = FastAPI(title="LocalMind Collective - Oxford AI Summit Demo")

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Global state
orchestrator = PresentationOrchestrator()
connections = set()
is_processing = False

# Demo scenarios matching slides
DEMO_SCENARIOS = [
    {
        "id": "quantum",
        "title": "What is quantum computing?",
        "description": "Simple query demonstration (30 seconds)",
        "query": "What is quantum computing?",
        "mode": "simple",
        "expected_time": "~30s",
        "agents": ["Web Harvester"],
        "highlights": ["Basic single-agent research", "Fast response", "Clear explanation"]
    },
    {
        "id": "mrna",
        "title": "mRNA vaccine mechanisms",
        "description": "Complex multi-agent analysis (2 minutes)",
        "query": "Analyze mRNA vaccine mechanisms, efficacy data, and therapeutic applications",
        "mode": "expert",
        "expected_time": "~2min",
        "agents": ["Domain Specialist", "Web Harvester", "Fact Validator"],
        "highlights": ["Multi-agent collaboration", "Expert domain analysis", "Fact validation"]
    },
    {
        "id": "ai_safety",
        "title": "AI safety developments",
        "description": "Current events research with web search",
        "query": "What are the latest developments in AI safety and alignment research?",
        "mode": "auto",
        "expected_time": "~1min",
        "agents": ["Web Harvester", "Domain Specialist"],
        "highlights": ["Real-time web search", "Current information", "Domain expertise"]
    },
    {
        "id": "local_ai",
        "title": "Local AI deployment",
        "description": "Technical analysis with quality audit",
        "query": "How to deploy enterprise AI systems locally with quantized models?",
        "mode": "expert",
        "expected_time": "~90s",
        "agents": ["Domain Specialist", "Web Harvester", "Quality Auditor"],
        "highlights": ["Technical depth", "Practical guidance", "Quality assessment"]
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
            await websocket.send_json(update)
        
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
            
        except Exception as e:
            logger.error(f"Demo error: {e}")
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
    
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
    
    return {
        "platform": f"{platform.system()} {platform.release()}",
        "processor": platform.processor() or platform.machine(),
        "gpu": gpu_info,
        "vram": vram_info,
        "cpu_cores": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "brave_api": "Active" if os.getenv("BRAVE_API_KEY") else "Not configured",
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
    
    print("\n" + "="*60)
    print("🚀 LocalMind Collective - Oxford AI Summit 2025 Demo")
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