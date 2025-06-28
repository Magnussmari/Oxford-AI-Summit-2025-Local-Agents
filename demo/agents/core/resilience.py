"""
Resilience patterns for robust agent execution
"""

import asyncio
from typing import Any, Optional, Dict, Callable
from datetime import datetime
import json
from loguru import logger


class ResilientAgentWrapper:
    """Wrap agents with resilience patterns - retry, fallback, circuit breaker"""
    
    def __init__(self, agent, retry_count: int = 3, timeout_multiplier: float = 1.5):
        self.agent = agent
        self.retry_count = retry_count
        self.timeout_multiplier = timeout_multiplier
        self.fallback_responses = {}
        self.error_history = []
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = 300  # 5 minutes
        self.circuit_open = False
        self.circuit_opened_at = None
        
    async def run_with_resilience(self, prompt: str, stream_callback=None, 
                                 validation_fn: Optional[Callable] = None) -> str:
        """Execute with retry logic, fallbacks, and circuit breaker"""
        
        # Check circuit breaker
        if self._is_circuit_open():
            logger.warning(f"Circuit breaker open for {self.agent.name}")
            return self._get_fallback_response("circuit_breaker")
            
        original_timeout = self.agent.timeout
        
        for attempt in range(self.retry_count):
            try:
                # Increase timeout with each retry
                self.agent.timeout = int(original_timeout * (self.timeout_multiplier ** attempt))
                
                # Add retry context to prompt if not first attempt
                enhanced_prompt = prompt
                if attempt > 0:
                    enhanced_prompt = self._add_retry_context(prompt, attempt)
                    logger.info(f"Retry {attempt + 1}/{self.retry_count} for {self.agent.name}")
                
                # Execute agent
                result = await self.agent.run(enhanced_prompt, stream_callback)
                
                # Validate response if validation function provided
                if validation_fn:
                    if not validation_fn(result):
                        logger.warning(f"Validation failed for {self.agent.name} on attempt {attempt + 1}")
                        if attempt < self.retry_count - 1:
                            continue
                        else:
                            return self._handle_validation_failure(result)
                
                # Success - reset circuit breaker
                self._reset_circuit_breaker()
                self.agent.timeout = original_timeout
                return result
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {self.agent.name} on attempt {attempt + 1}")
                self._record_error("timeout")
                
                if attempt < self.retry_count - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    return self._get_fallback_response("timeout")
                    
            except Exception as e:
                logger.error(f"Error for {self.agent.name} on attempt {attempt + 1}: {e}")
                self._record_error(str(e))
                
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return self._get_fallback_response("error", str(e))
        
        # Should not reach here, but just in case
        self.agent.timeout = original_timeout
        return self._get_fallback_response("max_retries")
    
    def _add_retry_context(self, prompt: str, attempt: int) -> str:
        """Add retry context to help the model succeed"""
        retry_hints = [
            "\n\n(Note: Previous attempt may have failed. Please ensure your response follows the exact format specified.)",
            "\n\n(Important: This is retry attempt {}. Please carefully follow all instructions and format requirements.)",
            "\n\n(CRITICAL: Final attempt. Please provide a properly formatted response according to the specifications.)"
        ]
        
        if attempt < len(retry_hints):
            return prompt + retry_hints[attempt - 1].format(attempt + 1)
        return prompt + retry_hints[-1]
    
    def _handle_validation_failure(self, result: str) -> str:
        """Handle validation failures gracefully"""
        # Try to extract useful content even if format is wrong
        logger.warning(f"Attempting to salvage response from {self.agent.name}")
        
        # For JSON responses, try to fix common issues
        if "{" in result and "}" in result:
            # Try to extract JSON even if surrounded by text
            import re
            json_match = re.search(r'\{[^{}]*\}', result, re.DOTALL)
            if json_match:
                try:
                    json.loads(json_match.group())
                    return json_match.group()
                except:
                    pass
        
        # Return the original result with a warning
        return f"[Warning: Response format validation failed]\n{result}"
    
    def _get_fallback_response(self, reason: str, error: str = None) -> str:
        """Get appropriate fallback response"""
        agent_role = self.agent.role
        
        fallbacks = {
            "timeout": {
                "orchestrator": json.dumps({
                    "complexity": "moderate",
                    "domain": "general",
                    "agents_needed": ["Domain Specialist", "Web Harvester"],
                    "strategy": "parallel",
                    "key_aspects": ["main topic", "current information"],
                    "fallback": True,
                    "reason": "timeout"
                }),
                "researcher": "Unable to complete research due to timeout. The query appears to require further investigation.",
                "validator": "Unable to validate claims due to timeout. Recommend manual verification.",
                "default": f"{self.agent.name} was unable to complete the task due to timeout."
            },
            "error": {
                "orchestrator": json.dumps({
                    "complexity": "complex",
                    "domain": "general", 
                    "agents_needed": ["Domain Specialist", "Web Harvester", "Fact Validator"],
                    "strategy": "sequential",
                    "key_aspects": ["comprehensive analysis needed"],
                    "fallback": True,
                    "reason": f"error: {error}"
                }),
                "default": f"{self.agent.name} encountered an error. Please try a simpler query."
            },
            "circuit_breaker": {
                "default": f"{self.agent.name} is temporarily unavailable due to repeated failures. Using cached response."
            },
            "max_retries": {
                "default": f"{self.agent.name} could not complete after {self.retry_count} attempts."
            }
        }
        
        fallback_set = fallbacks.get(reason, fallbacks["error"])
        return fallback_set.get(agent_role, fallback_set.get("default", "Fallback response"))
    
    def _record_error(self, error: str):
        """Record error for circuit breaker pattern"""
        self.error_history.append({
            "timestamp": datetime.now(),
            "error": error
        })
        
        # Keep only recent errors (last 10 minutes)
        cutoff = datetime.now().timestamp() - 600
        self.error_history = [
            e for e in self.error_history 
            if e["timestamp"].timestamp() > cutoff
        ]
        
        # Check if circuit should be opened
        if len(self.error_history) >= self.circuit_breaker_threshold:
            self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit breaker"""
        self.circuit_open = True
        self.circuit_opened_at = datetime.now()
        logger.warning(f"Circuit breaker opened for {self.agent.name}")
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker on success"""
        if self.error_history:
            self.error_history.clear()
        if self.circuit_open:
            self.circuit_open = False
            self.circuit_opened_at = None
            logger.info(f"Circuit breaker reset for {self.agent.name}")
    
    def _is_circuit_open(self) -> bool:
        """Check if circuit is open and should remain open"""
        if not self.circuit_open:
            return False
            
        # Check if enough time has passed to try again
        if self.circuit_opened_at:
            elapsed = (datetime.now() - self.circuit_opened_at).seconds
            if elapsed > self.circuit_breaker_reset_time:
                # Try to close circuit
                self.circuit_open = False
                logger.info(f"Circuit breaker attempting reset for {self.agent.name}")
                return False
                
        return True


class AgentHealthMonitor:
    """Monitor agent health and performance"""
    
    def __init__(self):
        self.agent_metrics = {}
        
    def record_execution(self, agent_name: str, success: bool, 
                        execution_time: float, tokens: int = 0):
        """Record agent execution metrics"""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_time": 0,
                "total_tokens": 0,
                "error_types": {}
            }
            
        metrics = self.agent_metrics[agent_name]
        metrics["total_executions"] += 1
        metrics["total_time"] += execution_time
        metrics["total_tokens"] += tokens
        
        if success:
            metrics["successful_executions"] += 1
        else:
            metrics["failed_executions"] += 1
            
    def get_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """Get health metrics for an agent"""
        if agent_name not in self.agent_metrics:
            return {"status": "healthy", "success_rate": 1.0}
            
        metrics = self.agent_metrics[agent_name]
        total = metrics["total_executions"]
        
        if total == 0:
            return {"status": "healthy", "success_rate": 1.0}
            
        success_rate = metrics["successful_executions"] / total
        avg_time = metrics["total_time"] / total
        
        # Determine health status
        if success_rate >= 0.95:
            status = "healthy"
        elif success_rate >= 0.8:
            status = "degraded"
        else:
            status = "unhealthy"
            
        return {
            "status": status,
            "success_rate": success_rate,
            "average_execution_time": avg_time,
            "total_executions": total,
            "failed_executions": metrics["failed_executions"]
        }


class FallbackChain:
    """Chain of fallback strategies for agents"""
    
    def __init__(self):
        self.strategies = []
        
    def add_strategy(self, name: str, handler: Callable):
        """Add a fallback strategy"""
        self.strategies.append((name, handler))
        
    async def execute(self, *args, **kwargs) -> Any:
        """Execute strategies in order until one succeeds"""
        errors = []
        
        for name, handler in self.strategies:
            try:
                logger.info(f"Attempting strategy: {name}")
                result = await handler(*args, **kwargs)
                if result is not None:
                    return result
            except Exception as e:
                logger.warning(f"Strategy {name} failed: {e}")
                errors.append((name, str(e)))
                continue
                
        # All strategies failed
        raise Exception(f"All fallback strategies failed: {errors}")