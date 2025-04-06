"""
GPU acceleration capabilities for SecureEraser.

This module provides optional GPU acceleration for file wiping operations
when supported by the system. It automatically falls back to CPU operations
when GPU acceleration is not available.
"""

import os
import logging
import tempfile
import time
from typing import Optional, Dict, Any, Tuple, List, Union

class GPUAccelerator:
    """
    Provides GPU acceleration for data wiping when available.
    Uses CUDA if available, or falls back to CPU operations.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the GPU accelerator, checking for CUDA availability.
        
        Args:
            logger: Logger instance to use.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.has_cuda = False
        self.is_available = False
        self.device_info = {}
        
        # Check for GPU acceleration capabilities
        try:
            # Try to import CUDA-related libraries
            try:
                import pycuda.driver as cuda
                import pycuda.autoinit
                import numpy as np
                self.has_cuda = True
                
                # Store references to avoid repeated imports
                self.cuda = cuda
                self.np = np
                
                # Get GPU device information
                device = cuda.Device(0)  # Use first device
                self.device_info = {
                    "name": device.name(),
                    "compute_capability": device.compute_capability(),
                    "total_memory": device.total_memory() // (1024 * 1024)  # MB
                }
                self.is_available = True
                
                self.logger.info(f"GPU acceleration enabled using {self.device_info['name']}")
                self.logger.debug(f"GPU memory: {self.device_info['total_memory']}MB")
                
            except ImportError:
                self.has_cuda = False
                self.logger.info("GPU acceleration not available: PyCUDA not installed")
            except Exception as e:
                self.has_cuda = False
                self.logger.info(f"GPU acceleration not available: {e}")
                
        except Exception as e:
            self.logger.warning(f"Error checking for GPU acceleration: {e}")
            self.is_available = False
    
    def generate_secure_data(self, pattern: Union[bytes, None], size: int) -> bytes:
        """
        Generate secure data for wiping, using GPU if available.
        
        Args:
            pattern: Optional pattern to use (if None, random data is generated)
            size: Size of data to generate in bytes
            
        Returns:
            Generated data as bytes
        """
        if not self.is_available:
            # Fall back to CPU-based generation
            import random
            if pattern:
                # Repeat pattern to fill the requested size
                return (pattern * (size // len(pattern) + 1))[:size]
            else:
                # Generate random data
                return bytes(random.getrandbits(8) for _ in range(size))
        
        try:
            # Use GPU to generate data
            import numpy as np
            
            if pattern:
                # Convert pattern to numpy array
                pattern_array = np.frombuffer(pattern, dtype=np.uint8)
                # Create a GPU array to store the output
                result = np.zeros(size, dtype=np.uint8)
                
                # Fill the result with the pattern
                for i in range(0, size, len(pattern_array)):
                    end = min(i + len(pattern_array), size)
                    slice_size = end - i
                    result[i:end] = pattern_array[:slice_size]
                
                return result.tobytes()
            else:
                # Generate random data on GPU
                # Allocate GPU memory
                import pycuda.gpuarray as gpuarray
                import pycuda.curandom
                
                # Generate random data on GPU
                rng = pycuda.curandom.XORWOWRandomNumberGenerator()
                gpu_result = rng.gen_uniform(size, dtype=np.uint8)
                
                # Convert to bytes
                return gpu_result.get().tobytes()
                
        except Exception as e:
            self.logger.warning(f"GPU data generation failed, falling back to CPU: {e}")
            # Fall back to CPU
            import random
            if pattern:
                return (pattern * (size // len(pattern) + 1))[:size]
            else:
                return bytes(random.getrandbits(8) for _ in range(size))
    
    def wipe_file_with_gpu(self, file_path: str, pattern: Optional[bytes] = None, 
                          chunk_size: int = 1024*1024*10) -> bool:
        """
        Wipe a file using GPU acceleration (if available).
        
        Args:
            file_path: Path to the file to wipe
            pattern: Optional pattern to use (if None, random data is used)
            chunk_size: Size of each chunk to process at once
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.logger.error(f"File {file_path} does not exist or is not a file")
            return False
            
        try:
            file_size = os.path.getsize(file_path)
            
            # Skip empty files
            if file_size == 0:
                return True
                
            self.logger.debug(f"Wiping {file_path} with GPU acceleration (size: {file_size} bytes)")
            
            # Wipe the file in chunks
            with open(file_path, 'wb') as f:
                remaining_size = file_size
                
                while remaining_size > 0:
                    current_chunk = min(chunk_size, remaining_size)
                    
                    # Generate secure data using GPU
                    data = self.generate_secure_data(pattern, current_chunk)
                    
                    # Write to file
                    f.write(data)
                    
                    # Update remaining size
                    remaining_size -= current_chunk
            
            # Flush to disk
            os.sync()
            return True
            
        except Exception as e:
            self.logger.error(f"Error in GPU wiping: {e}")
            return False
    
    def get_acceleration_status(self) -> Dict[str, Any]:
        """
        Get the current acceleration status.
        
        Returns:
            Dictionary with acceleration details
        """
        status = {
            "gpu_available": self.is_available,
            "has_cuda": self.has_cuda,
            "device_info": self.device_info
        }
        
        # Run a quick performance test if GPU is available
        if self.is_available:
            # Generate 100MB of data and measure time
            start_time = time.time()
            self.generate_secure_data(None, 100 * 1024 * 1024)
            gpu_time = time.time() - start_time
            
            # Do the same with CPU
            start_time = time.time()
            import random
            cpu_data = bytes(random.getrandbits(8) for _ in range(100 * 1024 * 1024))
            cpu_time = time.time() - start_time
            
            status["performance_test"] = {
                "gpu_time": gpu_time,
                "cpu_time": cpu_time,
                "speedup": cpu_time / gpu_time if gpu_time > 0 else 0
            }
            
        return status