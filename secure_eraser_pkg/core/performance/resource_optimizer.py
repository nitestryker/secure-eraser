"""
Resource optimization for improved performance.

This module provides automatic resource optimization based on system capabilities.
It dynamically adjusts chunk sizes, thread counts, and other parameters based on
the available system resources.
"""

import os
import psutil
import logging
import time
from typing import Dict, Any, Optional, Tuple

class ResourceOptimizer:
    """
    Dynamically optimizes resource usage based on system capabilities.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the resource optimizer.
        
        Args:
            logger: Logger instance to use.
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Cache system info
        self._system_info = self._get_system_info()
        self.logger.debug(f"System info: {self._system_info}")
        
        # Default optimization parameters
        self._defaults = {
            "chunk_size": 1024 * 1024 * 10,  # 10 MB
            "max_workers": max(1, psutil.cpu_count(logical=False) or 2 - 1),
            "io_priority": psutil.IOPRIO_CLASS_NORMAL
        }
        
        # Initialize optimization state
        self._current_optimizations = self._defaults.copy()
        
        # Adjustment factors
        self._adjustment_factors = {
            "memory_pressure": 1.0,
            "cpu_load": 1.0,
            "io_pressure": 1.0
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """
        Get current system resource information.
        
        Returns:
            Dictionary with system resource information
        """
        try:
            memory = psutil.virtual_memory()
            cpu_count = psutil.cpu_count(logical=False) or 2
            
            # Get I/O stats
            try:
                disk_io = psutil.disk_io_counters()
            except Exception:
                disk_io = None
                
            return {
                "cpu": {
                    "physical_cores": cpu_count,
                    "logical_cores": psutil.cpu_count(logical=True) or cpu_count,
                    "usage_percent": psutil.cpu_percent(interval=0.1)
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used_percent": memory.percent
                },
                "disk": {
                    "io": disk_io
                }
            }
        except Exception as e:
            self.logger.warning(f"Error getting system info: {e}")
            # Return fallback values
            return {
                "cpu": {"physical_cores": 2, "logical_cores": 4, "usage_percent": 50},
                "memory": {"total": 8 * 1024**3, "available": 4 * 1024**3, "used_percent": 50},
                "disk": {"io": None}
            }
    
    def update_system_status(self) -> Dict[str, Any]:
        """
        Update system status and recalculate optimization parameters.
        
        Returns:
            Current optimization parameters
        """
        # Update system info
        self._system_info = self._get_system_info()
        
        # Calculate adjustment factors
        self._calculate_adjustment_factors()
        
        # Update optimization parameters
        self._update_optimizations()
        
        return self._current_optimizations
    
    def _calculate_adjustment_factors(self):
        """
        Calculate adjustment factors based on current system load.
        """
        # Memory pressure adjustment
        memory_percent = self._system_info["memory"]["used_percent"]
        if memory_percent > 90:
            self._adjustment_factors["memory_pressure"] = 0.5
        elif memory_percent > 80:
            self._adjustment_factors["memory_pressure"] = 0.7
        elif memory_percent > 70:
            self._adjustment_factors["memory_pressure"] = 0.8
        elif memory_percent < 30:
            self._adjustment_factors["memory_pressure"] = 1.2
        else:
            self._adjustment_factors["memory_pressure"] = 1.0
        
        # CPU load adjustment
        cpu_percent = self._system_info["cpu"]["usage_percent"]
        if cpu_percent > 90:
            self._adjustment_factors["cpu_load"] = 0.6
        elif cpu_percent > 80:
            self._adjustment_factors["cpu_load"] = 0.8
        elif cpu_percent < 20:
            self._adjustment_factors["cpu_load"] = 1.2
        else:
            self._adjustment_factors["cpu_load"] = 1.0
        
        # I/O pressure is hardest to measure - we'll use a simplified approach
        # and just use 1.0 as the default factor
        self._adjustment_factors["io_pressure"] = 1.0
    
    def _update_optimizations(self):
        """
        Update optimization parameters based on adjustment factors.
        """
        # Update chunk size based on memory pressure
        memory_factor = self._adjustment_factors["memory_pressure"]
        new_chunk_size = int(self._defaults["chunk_size"] * memory_factor)
        
        # Ensure chunk size stays within reasonable limits
        min_chunk_size = 1024 * 1024  # 1 MB
        max_chunk_size = 1024 * 1024 * 100  # 100 MB
        new_chunk_size = max(min_chunk_size, min(new_chunk_size, max_chunk_size))
        
        # Update max workers based on CPU load
        cpu_factor = self._adjustment_factors["cpu_load"]
        new_max_workers = max(1, int(self._defaults["max_workers"] * cpu_factor))
        
        # Update I/O priority based on I/O pressure
        io_factor = self._adjustment_factors["io_pressure"]
        if io_factor < 0.7:
            new_io_priority = psutil.IOPRIO_CLASS_IDLE
        elif io_factor > 1.2:
            new_io_priority = psutil.IOPRIO_CLASS_RT
        else:
            new_io_priority = psutil.IOPRIO_CLASS_NORMAL
        
        # Update current optimizations
        self._current_optimizations = {
            "chunk_size": new_chunk_size,
            "max_workers": new_max_workers,
            "io_priority": new_io_priority
        }
        
        self.logger.debug(f"Updated optimizations: {self._current_optimizations}")
    
    def get_optimal_chunk_size(self, file_size: Optional[int] = None) -> int:
        """
        Get the optimal chunk size for the given file size.
        
        Args:
            file_size: Size of the file to process (optional)
            
        Returns:
            Optimal chunk size in bytes
        """
        # Start with the current optimization
        chunk_size = self._current_optimizations["chunk_size"]
        
        # If file size is provided, we can further optimize
        if file_size is not None:
            # For small files, use smaller chunks
            if file_size < chunk_size * 10:
                # Use 1/10 of the file size but at least 1MB
                return max(1024 * 1024, file_size // 10)
            
            # For very large files, we might want to use larger chunks
            if file_size > chunk_size * 1000:
                # Increase chunk size for very large files, up to 100MB
                return min(1024 * 1024 * 100, chunk_size * 2)
        
        return chunk_size
    
    def get_optimal_worker_count(self, file_count: Optional[int] = None) -> int:
        """
        Get the optimal worker count for the given number of files.
        
        Args:
            file_count: Number of files to process (optional)
            
        Returns:
            Optimal worker count
        """
        worker_count = self._current_optimizations["max_workers"]
        
        # If file count is provided, we can further optimize
        if file_count is not None:
            # If we have very few files, reduce worker count
            if file_count < worker_count:
                return file_count
        
        return worker_count
    
    def set_io_priority(self):
        """
        Set the current process I/O priority based on optimization.
        """
        try:
            p = psutil.Process()
            p.ionice(self._current_optimizations["io_priority"])
        except Exception as e:
            self.logger.warning(f"Could not set I/O priority: {e}")
    
    def get_optimization_params(self) -> Dict[str, Any]:
        """
        Get the current optimization parameters.
        
        Returns:
            Dictionary with current optimization parameters
        """
        # Update the system status to ensure we have the latest info
        self.update_system_status()
        
        # Return both current optimizations and adjustment factors
        return {
            "optimizations": self._current_optimizations,
            "adjustment_factors": self._adjustment_factors,
            "system_info": self._system_info
        }