"""
Enhanced System Health Monitoring for Oxford AI Summit 2025
Comprehensive monitoring for live demo reliability
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
import psutil
import aiohttp
import structlog
from pathlib import Path

logger = structlog.get_logger()


@dataclass
class HealthStatus:
    """Health status for a component."""
    name: str
    healthy: bool
    message: str
    response_time: Optional[float] = None
    last_check: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_free_gb: float
    temperature_celsius: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


class HealthMonitor:
    """Enhanced health monitoring for live demos."""
    
    def __init__(self, settings):
        self.settings = settings
        self.health_history: List[Dict[str, HealthStatus]] = []
        self.metrics_history: List[SystemMetrics] = []
        self._monitoring = False
        
    async def start_monitoring(self, interval: int = 30):
        """Start continuous health monitoring."""
        self._monitoring = True
        logger.info("Starting health monitoring", interval=interval)
        
        while self._monitoring:
            try:
                await self.perform_health_check()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error("Health monitoring error", error=str(e))
                await asyncio.sleep(interval)
                
    def stop_monitoring(self):
        """Stop health monitoring."""
        self._monitoring = False
        logger.info("Stopped health monitoring")
        
    async def perform_health_check(self) -> Dict[str, HealthStatus]:
        """Perform comprehensive health check."""
        health_status = {}
        
        # Check Ollama service
        health_status["ollama"] = await self._check_ollama()
        
        # Check Brave API if configured
        if self.settings.brave_api_key:
            health_status["brave_api"] = await self._check_brave_api()
        
        # Check system resources
        health_status["system"] = self._check_system_resources()
        
        # Check model availability
        health_status["models"] = await self._check_model_availability()
        
        # Store history
        self.health_history.append(health_status)
        if len(self.health_history) > 100:  # Keep last 100 checks
            self.health_history.pop(0)
            
        # Store system metrics
        metrics = self._get_system_metrics()
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)
            
        logger.info("Health check completed", 
                   healthy_services=sum(1 for status in health_status.values() if status.healthy),
                   total_services=len(health_status))
        
        return health_status
        
    async def _check_ollama(self) -> HealthStatus:
        """Check Ollama service health."""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.settings.ollama_host}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        return HealthStatus(
                            name="ollama",
                            healthy=True,
                            message=f"Ollama healthy with {len(models)} models",
                            response_time=response_time,
                            metadata={"model_count": len(models)}
                        )
                    else:
                        return HealthStatus(
                            name="ollama",
                            healthy=False,
                            message=f"Ollama returned status {response.status}",
                            response_time=response_time
                        )
                        
        except asyncio.TimeoutError:
            return HealthStatus(
                name="ollama",
                healthy=False,
                message="Ollama connection timeout",
                response_time=time.time() - start_time
            )
        except Exception as e:
            return HealthStatus(
                name="ollama",
                healthy=False,
                message=f"Ollama connection failed: {str(e)}",
                response_time=time.time() - start_time
            )
            
    async def _check_brave_api(self) -> HealthStatus:
        """Check Brave API health."""
        start_time = time.time()
        
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.settings.brave_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.search.brave.com/res/v1/web/search?q=test&count=1",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return HealthStatus(
                            name="brave_api",
                            healthy=True,
                            message="Brave API healthy",
                            response_time=response_time
                        )
                    else:
                        return HealthStatus(
                            name="brave_api",
                            healthy=False,
                            message=f"Brave API returned status {response.status}",
                            response_time=response_time
                        )
                        
        except Exception as e:
            return HealthStatus(
                name="brave_api",
                healthy=False,
                message=f"Brave API check failed: {str(e)}",
                response_time=time.time() - start_time
            )
            
    def _check_system_resources(self) -> HealthStatus:
        """Check system resource health."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            memory_available_gb = memory.available / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            
            # Health criteria
            memory_healthy = memory_available_gb >= 2.0  # At least 2GB free
            disk_healthy = disk_free_gb >= 5.0  # At least 5GB free
            cpu_healthy = cpu_percent < 90  # CPU usage below 90%
            
            overall_healthy = memory_healthy and disk_healthy and cpu_healthy
            
            issues = []
            if not memory_healthy:
                issues.append(f"Low memory: {memory_available_gb:.1f}GB free")
            if not disk_healthy:
                issues.append(f"Low disk: {disk_free_gb:.1f}GB free")
            if not cpu_healthy:
                issues.append(f"High CPU: {cpu_percent:.1f}%")
                
            message = "System resources healthy" if overall_healthy else f"Issues: {', '.join(issues)}"
            
            return HealthStatus(
                name="system",
                healthy=overall_healthy,
                message=message,
                metadata={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory_available_gb,
                    "disk_free_gb": disk_free_gb
                }
            )
            
        except Exception as e:
            return HealthStatus(
                name="system",
                healthy=False,
                message=f"System check failed: {str(e)}"
            )
            
    async def _check_model_availability(self) -> HealthStatus:
        """Check if required models are available."""
        required_models = [
            "deepseek-r1:8b",
            "qwen3:8b",
            "qwen3:4b",
            "phi4-mini"
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.settings.ollama_host}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        available_models = [model["name"] for model in data.get("models", [])]
                        
                        missing_models = [model for model in required_models if model not in available_models]
                        
                        if not missing_models:
                            return HealthStatus(
                                name="models",
                                healthy=True,
                                message=f"All {len(required_models)} required models available",
                                metadata={
                                    "required_models": required_models,
                                    "available_models": available_models
                                }
                            )
                        else:
                            return HealthStatus(
                                name="models",
                                healthy=False,
                                message=f"Missing models: {', '.join(missing_models)}",
                                metadata={
                                    "required_models": required_models,
                                    "missing_models": missing_models,
                                    "available_models": available_models
                                }
                            )
                    else:
                        return HealthStatus(
                            name="models",
                            healthy=False,
                            message=f"Failed to check models: status {response.status}"
                        )
                        
        except Exception as e:
            return HealthStatus(
                name="models",
                healthy=False,
                message=f"Model check failed: {str(e)}"
            )
            
    def _get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent()
        
        # Try to get temperature (Linux/macOS specific)
        temperature = None
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get average temperature from available sensors
                    all_temps = []
                    for sensor_name, sensor_list in temps.items():
                        for sensor in sensor_list:
                            if sensor.current:
                                all_temps.append(sensor.current)
                    if all_temps:
                        temperature = sum(all_temps) / len(all_temps)
        except:
            pass  # Temperature monitoring not available
            
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_gb=memory.available / (1024**3),
            disk_free_gb=disk.free / (1024**3),
            temperature_celsius=temperature
        )
        
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        if not self.health_history:
            return {"status": "no_data", "message": "No health data available"}
            
        latest_health = self.health_history[-1]
        latest_metrics = self.metrics_history[-1] if self.metrics_history else None
        
        overall_healthy = all(status.healthy for status in latest_health.values())
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "services": {name: {
                "healthy": status.healthy,
                "message": status.message,
                "response_time": status.response_time,
                "last_check": status.last_check.isoformat()
            } for name, status in latest_health.items()},
            "metrics": {
                "cpu_percent": latest_metrics.cpu_percent,
                "memory_percent": latest_metrics.memory_percent,
                "memory_available_gb": latest_metrics.memory_available_gb,
                "disk_free_gb": latest_metrics.disk_free_gb,
                "temperature_celsius": latest_metrics.temperature_celsius
            } if latest_metrics else None,
            "history_length": len(self.health_history)
        }
        
    def export_metrics(self, filepath: Path):
        """Export metrics to file for analysis."""
        try:
            export_data = {
                "health_history": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "services": {name: {
                            "healthy": status.healthy,
                            "message": status.message,
                            "response_time": status.response_time,
                            "metadata": status.metadata
                        } for name, status in health_check.items()}
                    }
                    for health_check in self.health_history
                ],
                "metrics_history": [
                    {
                        "timestamp": metrics.timestamp.isoformat(),
                        "cpu_percent": metrics.cpu_percent,
                        "memory_percent": metrics.memory_percent,
                        "memory_available_gb": metrics.memory_available_gb,
                        "disk_free_gb": metrics.disk_free_gb,
                        "temperature_celsius": metrics.temperature_celsius
                    }
                    for metrics in self.metrics_history
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            logger.info("Metrics exported", filepath=str(filepath))
            
        except Exception as e:
            logger.error("Failed to export metrics", error=str(e))


# Thermal monitoring for live demos (macOS/Linux specific)
def get_system_thermal_info() -> Dict[str, Any]:
    """Get system thermal information."""
    thermal_info = {
        "temperature": None,
        "thermal_state": "unknown",
        "fan_speeds": []
    }
    
    try:
        # Try to get temperature information
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                all_temps = []
                for sensor_name, sensor_list in temps.items():
                    for sensor in sensor_list:
                        if sensor.current:
                            all_temps.append(sensor.current)
                            
                if all_temps:
                    avg_temp = sum(all_temps) / len(all_temps)
                    thermal_info["temperature"] = round(avg_temp, 1)
                    
                    # Determine thermal state
                    if avg_temp < 60:
                        thermal_info["thermal_state"] = "cool"
                    elif avg_temp < 80:
                        thermal_info["thermal_state"] = "warm"
                    else:
                        thermal_info["thermal_state"] = "hot"
        
        # Try to get fan information
        if hasattr(psutil, "sensors_fans"):
            fans = psutil.sensors_fans()
            if fans:
                for fan_name, fan_list in fans.items():
                    for fan in fan_list:
                        if fan.current:
                            thermal_info["fan_speeds"].append({
                                "name": fan_name,
                                "rpm": fan.current
                            })
                            
    except Exception as e:
        logger.debug("Thermal monitoring not available", error=str(e))
        
    return thermal_info
