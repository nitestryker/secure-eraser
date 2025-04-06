"""
Secure memory handling to prevent data leakage during wiping operations.

This module provides mechanisms to ensure that sensitive data never remains in 
memory longer than necessary and is properly cleared from RAM when done.
"""

import os
import sys
import ctypes
import logging
import platform
import mmap
import array
from typing import Dict, List, Optional, Union, Any, Callable

class SecureMemoryHandler:
    """
    Secure memory handling to prevent data leakage during wiping operations.
    
    Features:
    - Secure memory allocation for sensitive data
    - Memory locking to prevent paging to disk
    - Memory zeroing after use
    - Memory protection against core dumps
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the secure memory handler.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger or logging.getLogger(__name__)
        self._memory_buffers = {}
        self._is_windows = platform.system() == "Windows"
        self._is_linux = platform.system() == "Linux"
        self._is_macos = platform.system() == "Darwin"
        
        # Initialize platform-specific methods
        self._init_platform_specifics()
    
    def _init_platform_specifics(self) -> None:
        """
        Initialize platform-specific memory handling methods.
        """
        # Disable core dumps if possible
        if self._is_linux or self._is_macos:
            try:
                import resource
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                self.logger.debug("Core dumps disabled")
            except (ImportError, AttributeError, PermissionError) as e:
                self.logger.warning(f"Could not disable core dumps: {e}")
    
    def allocate_secure_buffer(self, size: int, buffer_id: str) -> Union[bytearray, memoryview]:
        """
        Allocate a secure memory buffer of specified size.
        
        Args:
            size: Size of the buffer in bytes
            buffer_id: Identifier for this buffer
            
        Returns:
            Memory buffer (bytearray or memoryview)
        """
        self.logger.debug(f"Allocating secure buffer of size {size} bytes with ID: {buffer_id}")
        
        try:
            # Create a bytearray or mmap depending on size
            if size > 1024 * 1024 * 10:  # 10MB
                # For large buffers, use mmap with MAP_LOCKED if available
                if self._is_linux:
                    # Try to use mmap with MAP_LOCKED
                    buffer = mmap.mmap(-1, size, mmap.MAP_PRIVATE)
                    # Try to lock the memory to prevent swapping
                    try:
                        if hasattr(buffer, 'mlock'):
                            buffer.mlock()
                    except Exception as e:
                        self.logger.warning(f"Could not lock memory: {e}")
                else:
                    # Regular mmap for other platforms
                    buffer = mmap.mmap(-1, size, mmap.MAP_PRIVATE)
            else:
                # For smaller buffers, use bytearray
                buffer = bytearray(size)
                
                # Try to lock the memory if on Linux or macOS
                if self._is_linux or self._is_macos:
                    try:
                        import ctypes.util
                        libc = ctypes.CDLL(ctypes.util.find_library('c'))
                        # Get address and lock it
                        addr = ctypes.addressof((ctypes.c_char * size).from_buffer(buffer))
                        if hasattr(libc, 'mlock'):
                            result = libc.mlock(addr, size)
                            if result != 0:
                                self.logger.warning(f"Memory lock failed with error code: {result}")
                    except Exception as e:
                        self.logger.warning(f"Could not lock memory: {e}")
            
            # Store the buffer and its metadata
            self._memory_buffers[buffer_id] = {
                "buffer": buffer,
                "size": size,
                "locked": True
            }
            
            return memoryview(buffer)
            
        except Exception as e:
            self.logger.error(f"Error allocating secure memory: {e}")
            # Fall back to standard bytearray
            buffer = bytearray(size)
            self._memory_buffers[buffer_id] = {
                "buffer": buffer,
                "size": size,
                "locked": False
            }
            return buffer
    
    def secure_free(self, buffer_id: str) -> bool:
        """
        Securely free a memory buffer by overwriting it with zeros and releasing it.
        
        Args:
            buffer_id: Identifier of the buffer to free
            
        Returns:
            True if successful, False otherwise
        """
        if buffer_id not in self._memory_buffers:
            self.logger.warning(f"Buffer {buffer_id} not found")
            return False
            
        buffer_info = self._memory_buffers[buffer_id]
        buffer = buffer_info["buffer"]
        size = buffer_info["size"]
        
        try:
            # Zero out the memory
            self._zero_memory(buffer, size)
            
            # Unlock if locked
            if buffer_info.get("locked", False):
                if isinstance(buffer, mmap.mmap):
                    if hasattr(buffer, 'munlock'):
                        buffer.munlock()
                else:
                    # Try to unlock with libc
                    if self._is_linux or self._is_macos:
                        try:
                            import ctypes.util
                            libc = ctypes.CDLL(ctypes.util.find_library('c'))
                            addr = ctypes.addressof((ctypes.c_char * size).from_buffer(buffer))
                            if hasattr(libc, 'munlock'):
                                libc.munlock(addr, size)
                        except Exception as e:
                            self.logger.warning(f"Could not unlock memory: {e}")
            
            # Close if mmap
            if isinstance(buffer, mmap.mmap):
                buffer.close()
                
            # Remove from tracking
            del self._memory_buffers[buffer_id]
            
            self.logger.debug(f"Securely freed buffer {buffer_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during secure free of buffer {buffer_id}: {e}")
            return False
    
    def _zero_memory(self, buffer: Union[bytearray, memoryview, mmap.mmap], size: int) -> None:
        """
        Overwrite memory with zeros to remove sensitive data.
        
        Args:
            buffer: Memory buffer to zero
            size: Size of the buffer
        """
        try:
            # If buffer is a memoryview, get its underlying object
            actual_buffer = buffer.obj if isinstance(buffer, memoryview) else buffer
            
            if isinstance(actual_buffer, mmap.mmap):
                # For mmap objects
                actual_buffer.seek(0)
                actual_buffer.write(b'\x00' * size)
                actual_buffer.flush()
            else:
                # For bytearrays and similar
                for i in range(len(actual_buffer)):
                    actual_buffer[i] = 0
                    
            # Force flush CPU caches if possible
            self._flush_cpu_cache()
            
        except Exception as e:
            self.logger.error(f"Error zeroing memory: {e}")
    
    def _flush_cpu_cache(self) -> None:
        """
        Attempt to flush CPU caches to ensure zeroing is complete.
        This is platform-specific and may not work on all systems.
        """
        # Force garbage collection
        import gc
        gc.collect()
        
        # On Linux, try to use various techniques
        if self._is_linux:
            try:
                # Try a memory barrier instruction
                import ctypes
                if hasattr(ctypes, 'mfence'):
                    ctypes.mfence()
            except Exception:
                pass
    
    def protect_memory_leaks(self) -> None:
        """
        Enable additional protections against memory leaks.
        - Disable core dumps
        - Set seccomp filters on Linux (if available)
        - Disable swap if running as root
        """
        if self._is_linux:
            try:
                # Try to set seccomp filter to prevent certain syscalls
                try:
                    import seccomp
                    filter = seccomp.SyscallFilter(seccomp.KILL)
                    # Allow basic syscalls but block potentially dangerous ones
                    filter.add_rule(seccomp.ALLOW, "read")
                    filter.add_rule(seccomp.ALLOW, "write")
                    filter.add_rule(seccomp.ALLOW, "open")
                    filter.add_rule(seccomp.ALLOW, "close")
                    filter.add_rule(seccomp.ALLOW, "fstat")
                    filter.add_rule(seccomp.ALLOW, "mmap")
                    filter.add_rule(seccomp.ALLOW, "munmap")
                    filter.add_rule(seccomp.ALLOW, "exit")
                    # Block core dump and related syscalls
                    filter.add_rule(seccomp.KILL, "ptrace")
                    filter.load()
                    self.logger.debug("Seccomp filters enabled")
                except ImportError:
                    self.logger.debug("Seccomp not available")
                
                # If running as root, try to disable swap temporarily
                if os.geteuid() == 0:
                    try:
                        os.system("swapoff -a")
                        self.logger.debug("Swap disabled (will be re-enabled at process exit)")
                        # Register to re-enable swap at exit
                        import atexit
                        atexit.register(lambda: os.system("swapon -a"))
                    except Exception as e:
                        self.logger.warning(f"Could not disable swap: {e}")
                        
            except Exception as e:
                self.logger.warning(f"Error setting up memory leak protections: {e}")
    
    def clean_all_buffers(self) -> None:
        """
        Clean all secure memory buffers.
        """
        buffer_ids = list(self._memory_buffers.keys())
        for buffer_id in buffer_ids:
            self.secure_free(buffer_id)
            
    def secure_memcpy(self, 
                     dest_buffer_id: str, 
                     dest_offset: int,
                     src_buffer_id: str,
                     src_offset: int,
                     length: int) -> bool:
        """
        Securely copy memory between secure buffers.
        
        Args:
            dest_buffer_id: Destination buffer ID
            dest_offset: Offset in destination buffer
            src_buffer_id: Source buffer ID
            src_offset: Offset in source buffer
            length: Length of data to copy
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if dest_buffer_id not in self._memory_buffers:
                self.logger.error(f"Destination buffer {dest_buffer_id} not found")
                return False
                
            if src_buffer_id not in self._memory_buffers:
                self.logger.error(f"Source buffer {src_buffer_id} not found")
                return False
            
            dest_info = self._memory_buffers[dest_buffer_id]
            src_info = self._memory_buffers[src_buffer_id]
            
            dest_buffer = dest_info["buffer"]
            src_buffer = src_info["buffer"]
            
            # Check bounds
            if dest_offset + length > dest_info["size"]:
                self.logger.error("Destination buffer overflow")
                return False
                
            if src_offset + length > src_info["size"]:
                self.logger.error("Source buffer overflow")
                return False
            
            # Copy data
            if isinstance(dest_buffer, mmap.mmap) and isinstance(src_buffer, mmap.mmap):
                # mmap to mmap
                dest_buffer.seek(dest_offset)
                src_buffer.seek(src_offset)
                dest_buffer.write(src_buffer.read(length))
            elif isinstance(dest_buffer, mmap.mmap):
                # bytes/bytearray to mmap
                dest_buffer.seek(dest_offset)
                dest_buffer.write(bytes(src_buffer[src_offset:src_offset+length]))
            elif isinstance(src_buffer, mmap.mmap):
                # mmap to bytes/bytearray
                src_buffer.seek(src_offset)
                data = src_buffer.read(length)
                for i in range(length):
                    dest_buffer[dest_offset + i] = data[i]
            else:
                # bytes/bytearray to bytes/bytearray
                for i in range(length):
                    dest_buffer[dest_offset + i] = src_buffer[src_offset + i]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during secure memcpy: {e}")
            return False

    def __del__(self):
        """
        Clean up all secure memory allocations when the object is destroyed.
        """
        self.clean_all_buffers()

class SecureStringHandler:
    """
    Handle secure string operations to prevent sensitive data exposure.
    """
    
    def __init__(self, memory_handler: Optional[SecureMemoryHandler] = None,
                logger: Optional[logging.Logger] = None):
        """
        Initialize secure string handler.
        
        Args:
            memory_handler: SecureMemoryHandler instance to use
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.memory_handler = memory_handler or SecureMemoryHandler(logger)
        self._strings = {}
        self._string_counter = 0
    
    def create_secure_string(self, data: str) -> str:
        """
        Create a secure string that will be stored in protected memory.
        
        Args:
            data: String data to store securely
            
        Returns:
            ID reference to the secure string
        """
        # Convert string to bytes
        bytes_data = data.encode('utf-8')
        length = len(bytes_data)
        
        # Generate a unique ID
        string_id = f"secstr_{self._string_counter}"
        self._string_counter += 1
        
        # Allocate secure memory for the string
        buffer = self.memory_handler.allocate_secure_buffer(length, string_id)
        
        # Copy string data to buffer
        for i in range(length):
            buffer[i] = bytes_data[i]
        
        # Store metadata
        self._strings[string_id] = {
            "buffer_id": string_id,
            "length": length
        }
        
        # Clear original data from memory if possible
        # (note: this isn't guaranteed due to Python's string handling)
        del bytes_data
        
        return string_id
    
    def get_secure_string(self, string_id: str) -> Optional[str]:
        """
        Retrieve the secure string value (use sparingly).
        
        Args:
            string_id: ID of the secure string
            
        Returns:
            String value or None if not found
        """
        if string_id not in self._strings:
            self.logger.warning(f"Secure string {string_id} not found")
            return None
            
        string_info = self._strings[string_id]
        buffer_id = string_info["buffer_id"]
        
        if buffer_id not in self.memory_handler._memory_buffers:
            self.logger.error(f"Buffer {buffer_id} not found")
            return None
            
        buffer_info = self.memory_handler._memory_buffers[buffer_id]
        buffer = buffer_info["buffer"]
        length = string_info["length"]
        
        # Create a temporary bytes object and convert to string
        try:
            if isinstance(buffer, mmap.mmap):
                buffer.seek(0)
                result = buffer.read(length).decode('utf-8')
            else:
                result = bytes(buffer[:length]).decode('utf-8')
            return result
        except Exception as e:
            self.logger.error(f"Error retrieving secure string: {e}")
            return None
    
    def delete_secure_string(self, string_id: str) -> bool:
        """
        Delete a secure string and release its memory.
        
        Args:
            string_id: ID of the secure string
            
        Returns:
            True if successful, False otherwise
        """
        if string_id not in self._strings:
            self.logger.warning(f"Secure string {string_id} not found")
            return False
            
        string_info = self._strings[string_id]
        buffer_id = string_info["buffer_id"]
        
        # Delete from memory handler
        success = self.memory_handler.secure_free(buffer_id)
        
        # Remove from tracking
        if success:
            del self._strings[string_id]
            
        return success
    
    def clean_all_strings(self) -> None:
        """
        Clean all secure strings.
        """
        string_ids = list(self._strings.keys())
        for string_id in string_ids:
            self.delete_secure_string(string_id)
    
    def __del__(self):
        """
        Clean up all secure strings when the object is destroyed.
        """
        self.clean_all_strings()