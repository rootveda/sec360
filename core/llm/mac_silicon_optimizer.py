#!/usr/bin/env python3
"""
Mac Silicon Optimizer for LLM Safety Training
Provides Mac Silicon specific optimizations and monitoring
"""

import os
import sys
import json
import platform
import subprocess
import psutil
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

@dataclass
class SystemInfo:
    architecture: str
    macos_version: str
    cpu_cores: int
    memory_gb: float
    gpu_info: str
    ollama_version: str
    python_version: str

class MacSiliconOptimizer:
    def __init__(self, config_file: str = "core/mac_silicon_config.json"):
        self.config = self._load_config(config_file)
        self.system_info = self._get_system_info()
        self.setup_logging()
        
    def _load_config(self, config_file: str) -> Dict:
        """Load Mac Silicon specific configuration"""
        default_config = {
            "platform": "mac_silicon",
            "optimization": {
                "memory_efficient": True,
                "gpu_acceleration": True,
                "metal_performance_shaders": True,
                "unified_memory_optimization": True
            },
            "ollama": {
                "base_url": "http://localhost:11434",
                "timeout": 30,
                "max_retries": 3,
                "preferred_models": [
                    "llama3.2:3b",
                    "codellama:7b",
                    "mistral:7b",
                    "phi3:3.8b",
                    "qwen2.5:3b",
                    "gemma2:2b"
                ],
                "model_parameters": {
                    "num_ctx": 4096,
                    "num_gpu": -1,
                    "num_thread": 8,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            },
            "performance": {
                "max_concurrent_requests": 4,
                "request_timeout": 60,
                "memory_limit_mb": 8192,
                "cpu_cores": 8,
                "gpu_layers": -1
            }
        }
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default_config
    
    def _get_system_info(self) -> SystemInfo:
        """Get detailed system information"""
        try:
            # Get macOS version
            macos_version = subprocess.check_output(
                ["sw_vers", "-productVersion"], text=True
            ).strip()
            
            # Get GPU info
            gpu_info = "Unknown"
            try:
                gpu_output = subprocess.check_output(
                    ["system_profiler", "SPDisplaysDataType"], text=True
                )
                if "Apple" in gpu_output:
                    gpu_info = "Apple Silicon GPU"
                elif "AMD" in gpu_output:
                    gpu_info = "AMD GPU"
                elif "NVIDIA" in gpu_output:
                    gpu_info = "NVIDIA GPU"
            except:
                pass
            
            # Get Ollama version
            ollama_version = "Unknown"
            try:
                ollama_output = subprocess.check_output(
                    ["ollama", "--version"], text=True
                )
                ollama_version = ollama_output.strip()
            except:
                pass
            
            return SystemInfo(
                architecture=platform.machine(),
                macos_version=macos_version,
                cpu_cores=psutil.cpu_count(),
                memory_gb=psutil.virtual_memory().total / (1024**3),
                gpu_info=gpu_info,
                ollama_version=ollama_version,
                python_version=platform.python_version()
            )
        except Exception as e:
            logging.error(f"Error getting system info: {e}")
            return SystemInfo(
                architecture=platform.machine(),
                macos_version="Unknown",
                cpu_cores=psutil.cpu_count(),
                memory_gb=psutil.virtual_memory().total / (1024**3),
                gpu_info="Unknown",
                ollama_version="Unknown",
                python_version=platform.python_version()
            )
    
    def setup_logging(self):
        """Setup logging for the optimizer"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('core/logs/mac_silicon_optimizer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def is_mac_silicon(self) -> bool:
        """Check if running on Mac Silicon"""
        return self.system_info.architecture == "arm64" and platform.system() == "Darwin"
    
    def check_compatibility(self) -> Tuple[bool, List[str]]:
        """Check system compatibility"""
        issues = []
        
        if not self.is_mac_silicon():
            issues.append("Not running on Mac Silicon (ARM64)")
        
        # Check macOS version
        try:
            macos_version = float(self.system_info.macos_version.split('.')[0] + '.' + 
                                self.system_info.macos_version.split('.')[1])
            if macos_version < 12.0:
                issues.append(f"macOS version {self.system_info.macos_version} is too old (requires 12.0+)")
        except:
            issues.append("Could not determine macOS version")
        
        # Check Python version
        python_version = tuple(map(int, self.system_info.python_version.split('.')))
        if python_version < (3, 8):
            issues.append(f"Python version {self.system_info.python_version} is too old (requires 3.8+)")
        
        # Check memory
        if self.system_info.memory_gb < 8:
            issues.append(f"Insufficient memory: {self.system_info.memory_gb:.1f}GB (recommended: 8GB+)")
        
        return len(issues) == 0, issues
    
    def optimize_ollama_config(self) -> Dict:
        """Generate optimized Ollama configuration for Mac Silicon"""
        if not self.is_mac_silicon():
            return {}
        
        # Calculate optimal parameters based on system specs
        memory_gb = self.system_info.memory_gb
        cpu_cores = self.system_info.cpu_cores
        
        # Adjust context size based on available memory
        if memory_gb >= 16:
            num_ctx = 8192
        elif memory_gb >= 8:
            num_ctx = 4096
        else:
            num_ctx = 2048
        
        # Adjust thread count
        num_thread = min(cpu_cores, 8)
        
        config = {
            "num_ctx": num_ctx,
            "num_gpu": -1,  # Use all available GPU layers
            "num_thread": num_thread,
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "num_predict": -1,
            "stop": [],
            "stream": False
        }
        
        self.logger.info(f"Generated optimized Ollama config: {config}")
        return config
    
    def get_recommended_models(self) -> List[str]:
        """Get recommended models for Mac Silicon"""
        if not self.is_mac_silicon():
            return ["llama2:7b", "codellama:7b", "mistral:7b", "phi:3b"]
        
        memory_gb = self.system_info.memory_gb
        
        if memory_gb >= 16:
            # High-end Mac Silicon (M1 Pro/Max, M2 Pro/Max, M3 Pro/Max)
            return [
                "llama3.2:3b",      # Fast and efficient
                "codellama:7b",     # Code-specific
                "mistral:7b",       # General purpose
                "phi3:3.8b",        # Microsoft's efficient model
                "qwen2.5:3b",       # Alibaba's efficient model
                "gemma2:2b"         # Google's lightweight model
            ]
        elif memory_gb >= 8:
            # Standard Mac Silicon (M1, M2, M3)
            return [
                "llama3.2:3b",      # Fast and efficient
                "phi3:3.8b",        # Microsoft's efficient model
                "qwen2.5:3b",       # Alibaba's efficient model
                "gemma2:2b"         # Google's lightweight model
            ]
        else:
            # Low memory Mac Silicon
            return [
                "phi3:3.8b",        # Microsoft's efficient model
                "gemma2:2b"         # Google's lightweight model
            ]
    
    def monitor_performance(self) -> Dict:
        """Monitor system performance"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Temperature (if available)
            temperature = None
            try:
                # Try to get temperature from system
                temp_output = subprocess.check_output(
                    ["sudo", "powermetrics", "--samplers", "smc", "-n", "1", "-i", "1000"],
                    text=True, stderr=subprocess.DEVNULL, timeout=5
                )
                # Parse temperature from output (simplified)
                if "CPU die temperature" in temp_output:
                    temp_line = [line for line in temp_output.split('\n') if 'CPU die temperature' in line][0]
                    temperature = float(temp_line.split(':')[1].strip().split()[0])
            except:
                pass
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            performance_data = {
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": memory_available_gb,
                "temperature_celsius": temperature,
                "disk_percent": disk_percent,
                "system_info": {
                    "architecture": self.system_info.architecture,
                    "macos_version": self.system_info.macos_version,
                    "cpu_cores": self.system_info.cpu_cores,
                    "memory_gb": self.system_info.memory_gb,
                    "gpu_info": self.system_info.gpu_info
                }
            }
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error monitoring performance: {e}")
            return {}
    
    def optimize_system_settings(self) -> bool:
        """Optimize system settings for Mac Silicon"""
        if not self.is_mac_silicon():
            self.logger.warning("Not running on Mac Silicon, skipping optimizations")
            return False
        
        try:
            # Set environment variables for optimal performance
            os.environ["OLLAMA_NUM_PARALLEL"] = "4"
            os.environ["OLLAMA_MAX_LOADED_MODELS"] = "2"
            os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
            os.environ["OLLAMA_GPU_LAYERS"] = "-1"
            
            # Set Python optimizations
            os.environ["PYTHONOPTIMIZE"] = "1"
            os.environ["PYTHONUNBUFFERED"] = "1"
            
            self.logger.info("System settings optimized for Mac Silicon")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing system settings: {e}")
            return False
    
    def get_optimization_report(self) -> Dict:
        """Generate optimization report"""
        compatible, issues = self.check_compatibility()
        performance = self.monitor_performance()
        ollama_config = self.optimize_ollama_config()
        recommended_models = self.get_recommended_models()
        
        report = {
            "system_info": {
                "architecture": self.system_info.architecture,
                "macos_version": self.system_info.macos_version,
                "cpu_cores": self.system_info.cpu_cores,
                "memory_gb": self.system_info.memory_gb,
                "gpu_info": self.system_info.gpu_info,
                "ollama_version": self.system_info.ollama_version,
                "python_version": self.system_info.python_version
            },
            "compatibility": {
                "compatible": compatible,
                "issues": issues
            },
            "optimization": {
                "ollama_config": ollama_config,
                "recommended_models": recommended_models,
                "system_optimized": self.optimize_system_settings()
            },
            "performance": performance,
            "timestamp": time.time()
        }
        
        return report

def main():
    """Test the Mac Silicon optimizer"""
    optimizer = MacSiliconOptimizer()
    
    print("🍎 Mac Silicon Optimizer for LLM Safety Training")
    print("=" * 50)
    
    # Check compatibility
    compatible, issues = optimizer.check_compatibility()
    print(f"Compatibility: {'✅ Compatible' if compatible else '❌ Issues found'}")
    
    if issues:
        print("Issues:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Show system info
    print(f"\nSystem Information:")
    print(f"  Architecture: {optimizer.system_info.architecture}")
    print(f"  macOS Version: {optimizer.system_info.macos_version}")
    print(f"  CPU Cores: {optimizer.system_info.cpu_cores}")
    print(f"  Memory: {optimizer.system_info.memory_gb:.1f} GB")
    print(f"  GPU: {optimizer.system_info.gpu_info}")
    
    # Show recommended models
    print(f"\nRecommended Models:")
    for model in optimizer.get_recommended_models():
        print(f"  - {model}")
    
    # Show optimized config
    print(f"\nOptimized Ollama Config:")
    config = optimizer.optimize_ollama_config()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Generate full report
    report = optimizer.get_optimization_report()
    print(f"\nFull optimization report saved to logs/mac_silicon_optimizer.log")

if __name__ == "__main__":
    main()
