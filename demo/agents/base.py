"""
Base classes for all presentation agents with production enhancements
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from loguru import logger
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

# Core enhancement imports
from .core.prompting import StructuredPrompt, PromptValidator, PromptOptimizer
from .core.resilience import ResilientAgentWrapper
from .core.examples import PromptExampleBuilder
from .core.dynamic import AdaptiveTemperatureController, TokenOptimizer

# Load environment variables from root .env file
root_dir = Path(__file__).parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

CURRENT_DATE = datetime.now().strftime("%B %d, %Y")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


class PresentationAgent:
    """Enhanced base class with production features - resilience, optimization, and learning."""
    
    def __init__(self, name: str, model: str, role: str, temperature: float = 0.3):
        self.name = name
        self.model = model
        self.role = role
        self.base_temperature = temperature
        self.temperature = temperature
        self.timeout = 60  # Base timeout for streaming
        
        # Enhancement components
        self.prompt_validator = PromptValidator()
        self.prompt_optimizer = PromptOptimizer()
        self.token_optimizer = TokenOptimizer()
        self.temperature_controller = AdaptiveTemperatureController()
        self.example_builder = PromptExampleBuilder()
        
        # Performance tracking
        self.execution_history = []
        self.error_count = 0
        self.success_count = 0
        
    async def run(self, prompt: str, stream_callback=None, context: Dict[str, Any] = None) -> str:
        """Enhanced run method with optimization and adaptive behavior."""
        start_time = time.time()
        context = context or {}
        
        try:
            # Optimize prompt
            optimized_prompt = self._optimize_prompt(prompt, context)
            
            # Get adaptive temperature
            self.temperature = self._get_adaptive_temperature(context)
            
            # Send initial thinking update
            if stream_callback:
                await stream_callback({
                    "type": "agent_thinking",
                    "agent": self.name,
                    "model": self.model,
                    "temperature": self.temperature
                })
            
            # Use Ollama HTTP API for streaming
            url = f"{OLLAMA_HOST}/api/generate"
            payload = {
                "model": self.model,
                "prompt": optimized_prompt,
                "stream": True,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": context.get("max_tokens", 10000)
                }
            }
            
            full_response = ""
            token_count = 0
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    if 'response' in data:
                                        chunk = data['response']
                                        full_response += chunk
                                        # Only count tokens when we have word boundaries
                                        if chunk and (chunk[-1].isspace() or chunk[0].isspace()):
                                            token_count = len(full_response.split())
                                        
                                        # Stream the actual text to frontend
                                        if stream_callback and chunk:
                                            await stream_callback({
                                                "type": "agent_stream",
                                                "agent": self.name,
                                                "chunk": chunk,
                                                "tokens": token_count
                                            })
                                        
                                    if data.get('done', False):
                                        break
                                except json.JSONDecodeError:
                                    continue
                    else:
                        error_text = await response.text()
                        logger.error(f"{self.name} HTTP error {response.status}: {error_text}")
                        return f"Error: {self.name} failed with status {response.status}"
            
            # Send completion update
            if stream_callback:
                await stream_callback({
                    "type": "agent_response",
                    "agent": self.name,
                    "tokens": token_count,
                    "complete": True
                })
            
            # Record success
            execution_time = time.time() - start_time
            self._record_execution(True, execution_time, token_count)
            
            return full_response.strip()
            
        except asyncio.TimeoutError:
            logger.warning(f"{self.name} timed out after {self.timeout}s")
            self._record_execution(False, time.time() - start_time, 0)
            
            if stream_callback:
                await stream_callback({
                    "type": "agent_error",
                    "agent": self.name,
                    "error": "Timeout"
                })
            return f"{self.name} timed out. Consider using a smaller model."
            
        except aiohttp.ClientError as e:
            logger.error(f"{self.name} connection error: {e}")
            self._record_execution(False, time.time() - start_time, 0)
            
            if stream_callback:
                await stream_callback({
                    "type": "agent_error",
                    "agent": self.name,
                    "error": "Connection failed - Is Ollama running?"
                })
            return f"{self.name} connection error. Please ensure Ollama is running."
            
        except Exception as e:
            logger.error(f"{self.name} error: {e}")
            self._record_execution(False, time.time() - start_time, 0)
            
            if stream_callback:
                await stream_callback({
                    "type": "agent_error", 
                    "agent": self.name,
                    "error": str(e)
                })
            return f"{self.name} error: {str(e)}"
    
    def _optimize_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Optimize prompt based on context"""
        # Add examples if available
        if context.get("include_examples", True):
            examples_section = self.example_builder.build_examples_section(
                prompt, 
                self.role,
                include_complexity_match=True
            )
            if examples_section:
                prompt = f"{examples_section}\n\n{prompt}"
                
        # Compress if needed
        if context.get("compress_prompt", False):
            prompt = self.prompt_optimizer.compress_prompt(prompt)
            
        # Add format enforcement
        if context.get("response_format"):
            prompt = self.prompt_optimizer.add_format_enforcement(
                prompt, 
                context["response_format"]
            )
            
        return prompt
        
    def _get_adaptive_temperature(self, context: Dict[str, Any]) -> float:
        """Get adaptive temperature based on context"""
        return self.temperature_controller.get_optimal_temperature(
            agent_name=self.name,
            agent_type=self.role,
            query_type=context.get("query_type", "general"),
            previous_attempts=context.get("attempt", 0),
            performance_metrics=self.get_performance_metrics()
        )
        
    def _record_execution(self, success: bool, execution_time: float, tokens: int):
        """Record execution for performance tracking"""
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "execution_time": execution_time,
            "tokens": tokens
        })
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
            
        # Keep only recent history
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        total = self.success_count + self.error_count
        
        if total == 0:
            return {
                "success_rate": 1.0,
                "average_execution_time": 0,
                "average_tokens": 0,
                "total_executions": 0
            }
            
        recent_executions = self.execution_history[-10:] if self.execution_history else []
        
        return {
            "success_rate": self.success_count / total,
            "average_execution_time": sum(e["execution_time"] for e in recent_executions) / len(recent_executions) if recent_executions else 0,
            "average_tokens": sum(e["tokens"] for e in recent_executions) / len(recent_executions) if recent_executions else 0,
            "total_executions": total,
            "recent_trend": self._calculate_trend()
        }
        
    def _calculate_trend(self) -> str:
        """Calculate performance trend"""
        if len(self.execution_history) < 5:
            return "insufficient_data"
            
        recent = self.execution_history[-5:]
        older = self.execution_history[-10:-5] if len(self.execution_history) >= 10 else self.execution_history[:5]
        
        recent_success_rate = sum(1 for e in recent if e["success"]) / len(recent)
        older_success_rate = sum(1 for e in older if e["success"]) / len(older)
        
        if recent_success_rate > older_success_rate + 0.1:
            return "improving"
        elif recent_success_rate < older_success_rate - 0.1:
            return "degrading"
        else:
            return "stable"