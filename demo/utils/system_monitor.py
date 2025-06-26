"""
System monitoring utilities for macOS
Provides CPU temperature and fan speed monitoring
"""

import subprocess
import re
from typing import Dict, Any, Optional
import platform
from loguru import logger


class MacSystemMonitor:
    """Monitor system stats on macOS."""
    
    def __init__(self):
        self.is_mac = platform.system() == "Darwin"
        self.has_osx_cpu_temp = self._check_osx_cpu_temp()
        
    def _check_osx_cpu_temp(self) -> bool:
        """Check if osx-cpu-temp is available."""
        try:
            result = subprocess.run(["which", "osx-cpu-temp"], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature in Celsius."""
        if not self.is_mac:
            return None
            
        # Try osx-cpu-temp first
        if self.has_osx_cpu_temp:
            try:
                result = subprocess.run(
                    ["osx-cpu-temp", "-c"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    # Parse output like "58.5°C"
                    temp_str = result.stdout.strip()
                    temp_match = re.search(r'([\d.]+)', temp_str)
                    if temp_match:
                        return float(temp_match.group(1))
            except Exception as e:
                logger.debug(f"osx-cpu-temp failed: {e}")
        
        # Fallback to powermetrics (requires sudo)
        try:
            result = subprocess.run(
                ["sudo", "-n", "powermetrics", "--samplers", "smc", "-i", "1", "-n", "1"],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                # Parse CPU die temperature
                temp_match = re.search(r'CPU die temperature:\s+([\d.]+)\s+C', result.stdout)
                if temp_match:
                    return float(temp_match.group(1))
        except:
            pass
            
        return None
    
    def get_fan_speed(self) -> Optional[Dict[str, int]]:
        """Get fan speeds in RPM."""
        if not self.is_mac:
            return None
            
        # Try powermetrics (requires sudo)
        try:
            result = subprocess.run(
                ["sudo", "-n", "powermetrics", "--samplers", "smc", "-i", "1", "-n", "1"],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                fans = {}
                # Parse fan speeds
                fan_matches = re.findall(r'Fan\s+(\d+)\s+speed:\s+(\d+)\s+rpm', result.stdout)
                for fan_num, rpm in fan_matches:
                    fans[f"Fan {fan_num}"] = int(rpm)
                return fans if fans else None
        except:
            pass
            
        return None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get all available system stats."""
        stats = {
            "cpu_temp": None,
            "cpu_temp_unit": "°C",
            "fans": None,
            "available": False
        }
        
        temp = self.get_cpu_temperature()
        if temp is not None:
            stats["cpu_temp"] = round(temp, 1)
            stats["available"] = True
        
        fans = self.get_fan_speed()
        if fans:
            stats["fans"] = fans
            stats["available"] = True
            
        return stats


# Singleton instance
system_monitor = MacSystemMonitor()


def get_system_thermal_info() -> Dict[str, Any]:
    """Get thermal information for the current system."""
    return system_monitor.get_system_stats()