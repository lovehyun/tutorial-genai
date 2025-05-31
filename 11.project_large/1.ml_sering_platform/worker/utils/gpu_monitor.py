# worker/utils/gpu_monitor.py
import torch
import logging
import psutil
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GPUMonitor:
    """GPU and system resource monitoring"""
    
    @staticmethod
    def get_gpu_stats() -> Dict[str, Any]:
        """Get GPU statistics"""
        stats = {
            "gpu_available": torch.cuda.is_available(),
            "gpu_count": 0,
            "memory_allocated": 0,
            "memory_reserved": 0,
            "memory_total": 0
        }
        
        if torch.cuda.is_available():
            stats.update({
                "gpu_count": torch.cuda.device_count(),
                "memory_allocated": torch.cuda.memory_allocated() / 1e9,  # GB
                "memory_reserved": torch.cuda.memory_reserved() / 1e9,    # GB
                "memory_total": torch.cuda.get_device_properties(0).total_memory / 1e9,  # GB
                "gpu_name": torch.cuda.get_device_name(0)
            })
        
        return stats
    
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available": psutil.virtual_memory().available / 1e9,  # GB
            "memory_total": psutil.virtual_memory().total / 1e9,  # GB
            "disk_usage": psutil.disk_usage('/').percent
        }
    
    @staticmethod
    def log_resource_usage():
        """Log current resource usage"""
        gpu_stats = GPUMonitor.get_gpu_stats()
        sys_stats = GPUMonitor.get_system_stats()
        
        logger.info(f"GPU Memory: {gpu_stats['memory_allocated']:.2f}GB / {gpu_stats['memory_total']:.2f}GB")
        logger.info(f"System Memory: {sys_stats['memory_percent']:.1f}% | CPU: {sys_stats['cpu_percent']:.1f}%")
