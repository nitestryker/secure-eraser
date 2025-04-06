"""
Core eraser functionality for the SecureEraser tool.

This module implements the base secure erasure functionality.
"""

import os
import random
import logging
import tempfile
import time
import shutil
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


class SecureEraser:
    """
    Base class for secure file erasure operations.
    """
    
    # Wiping method patterns
    STANDARD_PASSES = 3  # Default pass count for standard method
    
    # DoD 5220.22-M standard wipe patterns
    DOD_PATTERNS = [
        b'\x00',                         # Pass 1: All zeros
        b'\xFF',                         # Pass 2: All ones
        b'\x00\xFF\x00\xFF\x00\xFF',     # Pass 3: Alternating bit pattern
    ]
    
    # Gutmann 35-pass method patterns (simplified representation)
    GUTMANN_PASSES = 35
    
    # Paranoid method (combination of multiple standards with extra passes)
    PARANOID_PASSES = 15
    
    def __init__(self, passes=3, method="standard", logger=None, **kwargs):
        """
        Initialize the secure eraser.
        
        Args:
            passes: Number of overwrite passes
            method: Wiping method (standard, dod, gutmann, paranoid)
            logger: Logger instance
            **kwargs: Additional arguments
        """
        self.passes = passes
        self.method = method
        self.logger = logger or logging.getLogger(__name__)
        
        # Set default pass count based on method if not explicitly specified
        if method == "dod" and passes == 3:
            self.passes = len(self.DOD_PATTERNS)
        elif method == "gutmann" and passes == 3:
            self.passes = self.GUTMANN_PASSES
        elif method == "paranoid" and passes == 3:
            self.passes = self.PARANOID_PASSES
    
    def secure_delete_file(self, file_path) -> bool:
        """
        Securely delete a file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            bool: Success or failure
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} does not exist")
            return False
            
        try:
            # Get file size for progress reporting
            file_size = os.path.getsize(file_path)
            
            # Open in read-write binary mode
            with open(file_path, "r+b") as f:
                # Apply the selected wiping method
                if self.method == "standard":
                    self._apply_standard_wipe(f, file_size)
                elif self.method == "dod":
                    self._apply_dod_wipe(f, file_size)
                elif self.method == "gutmann":
                    self._apply_gutmann_wipe(f, file_size)
                elif self.method == "paranoid":
                    self._apply_paranoid_wipe(f, file_size)
                elif self.method in ['nist_clear', 'nist_purge', 'dod_3pass', 'dod_7pass', 
                          'hmg_is5_baseline', 'hmg_is5_enhanced', 'navso', 
                          'afssi', 'ar_380_19', 'csc']:
                    # Military standards are handled in the SecureEraserWithVerification class
                    # This is just a placeholder for the base class
                    self._apply_standard_wipe(f, file_size)
                else:
                    # Default to standard wipe
                    self.logger.warning(f"Unknown wiping method '{self.method}', using standard")
                    self._apply_standard_wipe(f, file_size)
            
            # Truncate the file to 0 bytes
            with open(file_path, "w") as f:
                pass
                
            # Delete the file
            os.remove(file_path)
            
            self.logger.info(f"Successfully deleted file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def secure_delete_directory(self, directory_path) -> bool:
        """
        Securely delete a directory and all its contents.
        
        Args:
            directory_path: Path to the directory to delete
            
        Returns:
            bool: Success or failure
        """
        if not os.path.exists(directory_path):
            self.logger.error(f"Directory {directory_path} does not exist")
            return False
            
        try:
            # Walk the directory tree bottom-up to delete files first, then directories
            all_files = []
            all_dirs = []
            
            for root, dirs, files in os.walk(directory_path, topdown=False):
                # Add full paths of all files
                all_files.extend([os.path.join(root, file) for file in files])
                # Add directories for later removal
                all_dirs.append(root)
            
            # Process files in parallel for efficiency
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Map secure_delete_file to all files
                results = list(executor.map(self.secure_delete_file, all_files))
            
            # Check if all files were successfully deleted
            if not all(results) and len(results) > 0:
                self.logger.warning(f"Some files in {directory_path} could not be securely deleted")
            
            # Now remove all empty directories (from bottom up)
            for dir_path in all_dirs:
                if os.path.exists(dir_path):
                    try:
                        os.rmdir(dir_path)
                    except OSError as e:
                        self.logger.warning(f"Could not remove directory {dir_path}: {e}")
            
            # Final check if the root directory is gone
            if os.path.exists(directory_path):
                self.logger.warning(f"Directory {directory_path} still exists, trying to remove")
                try:
                    shutil.rmtree(directory_path)
                except Exception as e:
                    self.logger.error(f"Failed to remove directory {directory_path}: {e}")
                    return False
            
            self.logger.info(f"Successfully deleted directory: {directory_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting directory {directory_path}: {e}")
            return False
    
    def wipe_free_space(self, drive_path) -> bool:
        """
        Wipe free space on a drive.
        
        Args:
            drive_path: Path to the drive or mount point
            
        Returns:
            bool: Success or failure
        """
        if not os.path.exists(drive_path):
            self.logger.error(f"Drive path {drive_path} does not exist")
            return False
            
        try:
            # Create a temporary directory on the target drive
            temp_dir = tempfile.mkdtemp(dir=drive_path)
            self.logger.info(f"Created temporary directory for free space wiping: {temp_dir}")
            
            # Keep creating large files until the drive is full
            # Each iteration creates a 100MB file
            file_counter = 0
            file_size_mb = 100
            file_size_bytes = file_size_mb * 1024 * 1024
            
            while True:
                try:
                    # Create a new temporary file
                    temp_file = os.path.join(temp_dir, f"wipe_file_{file_counter}")
                    
                    with open(temp_file, "wb") as f:
                        # Apply standard wiping method to the temporary file
                        self._apply_standard_wipe(f, file_size_bytes)
                    
                    file_counter += 1
                    self.logger.debug(f"Created wiping file {file_counter} ({file_size_mb} MB)")
                    
                except Exception as e:
                    # If we can't create more files, the drive is likely full
                    self.logger.info(f"Drive filled or error occurred: {e}")
                    break
            
            # Securely delete all the temporary files
            self.logger.info(f"Securely deleting {file_counter} temporary files")
            self.secure_delete_directory(temp_dir)
            
            self.logger.info(f"Successfully wiped free space on: {drive_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error wiping free space on {drive_path}: {e}")
            return False
    
    def _apply_standard_wipe(self, file_obj, size):
        """
        Apply standard wiping method.
        
        Args:
            file_obj: File object to write to
            size: Size of the file in bytes
        """
        # Seek to beginning of file
        file_obj.seek(0)
        
        # Standard method: Multiple passes of random data
        for pass_num in range(1, self.passes + 1):
            self.logger.debug(f"Standard wipe pass {pass_num}/{self.passes}")
            
            # Seek to beginning of file for each pass
            file_obj.seek(0)
            
            # Write in chunks to handle large files
            bytes_written = 0
            chunk_size = min(1024 * 1024, size)  # 1 MB chunks or file size if smaller
            
            while bytes_written < size:
                # Generate random data for this chunk
                if bytes_written + chunk_size > size:
                    # Last chunk might be smaller
                    chunk_size = size - bytes_written
                
                # Generate random bytes
                random_data = os.urandom(chunk_size)
                
                # Write the chunk
                file_obj.write(random_data)
                
                # Flush to disk
                file_obj.flush()
                os.fsync(file_obj.fileno())
                
                bytes_written += chunk_size
            
        # Flush final writes
        file_obj.flush()
        os.fsync(file_obj.fileno())
    
    def _apply_dod_wipe(self, file_obj, size):
        """
        Apply DoD 5220.22-M wiping method.
        
        Args:
            file_obj: File object to write to
            size: Size of the file in bytes
        """
        # Seek to beginning of file
        file_obj.seek(0)
        
        # Apply each pattern in sequence
        for pass_num, pattern in enumerate(self.DOD_PATTERNS, 1):
            self.logger.debug(f"DoD wipe pass {pass_num}/{len(self.DOD_PATTERNS)}")
            
            # Seek to beginning of file for each pass
            file_obj.seek(0)
            
            # Create a chunk of the pattern to write
            chunk_size = min(1024 * 1024, size)  # 1 MB chunks or file size if smaller
            
            # Calculate number of repeats needed to fill the chunk size
            repeats = chunk_size // len(pattern) + 1
            chunk = (pattern * repeats)[:chunk_size]
            
            # Write in chunks to handle large files
            bytes_written = 0
            
            while bytes_written < size:
                # Last chunk might be smaller
                if bytes_written + len(chunk) > size:
                    chunk = chunk[:size - bytes_written]
                
                # Write the chunk
                file_obj.write(chunk)
                
                # Flush to disk
                file_obj.flush()
                os.fsync(file_obj.fileno())
                
                bytes_written += len(chunk)
        
        # Flush final writes
        file_obj.flush()
        os.fsync(file_obj.fileno())
    
    def _apply_gutmann_wipe(self, file_obj, size):
        """
        Apply Gutmann 35-pass wiping method.
        
        Args:
            file_obj: File object to write to
            size: Size of the file in bytes
        """
        # Gutmann's method includes 35 passes
        for pass_num in range(1, self.GUTMANN_PASSES + 1):
            self.logger.debug(f"Gutmann wipe pass {pass_num}/{self.GUTMANN_PASSES}")
            
            # Seek to beginning of file for each pass
            file_obj.seek(0)
            
            # Determine pattern for this pass
            if pass_num <= 4 or pass_num >= 32:
                # Random data for passes 1-4 and 32-35
                self._write_random_data(file_obj, size)
            else:
                # Fixed patterns for passes 5-31
                # Generate a specific pattern based on the pass number
                # This is a simplified version of Gutmann's patterns
                pattern = bytes([pass_num % 256]) * 256
                self._write_pattern(file_obj, pattern, size)
            
            # Flush after each pass
            file_obj.flush()
            os.fsync(file_obj.fileno())
    
    def _apply_paranoid_wipe(self, file_obj, size):
        """
        Apply paranoid wiping method (combination of multiple methods).
        
        Args:
            file_obj: File object to write to
            size: Size of the file in bytes
        """
        # Paranoid method combines DoD, random passes, and special patterns
        
        # First, apply DoD method
        self._apply_dod_wipe(file_obj, size)
        
        # Then add additional random passes
        for pass_num in range(1, self.PARANOID_PASSES - len(self.DOD_PATTERNS) + 1):
            self.logger.debug(f"Paranoid additional pass {pass_num}")
            
            # Seek to beginning of file for each pass
            file_obj.seek(0)
            
            # Write random data
            self._write_random_data(file_obj, size)
            
            # Flush after each pass
            file_obj.flush()
            os.fsync(file_obj.fileno())
    
    def _write_random_data(self, file_obj, size):
        """
        Write random data to a file.
        
        Args:
            file_obj: File object to write to
            size: Size of the file in bytes
        """
        # Write in chunks to handle large files
        bytes_written = 0
        chunk_size = min(1024 * 1024, size)  # 1 MB chunks or file size if smaller
        
        while bytes_written < size:
            # Generate random data for this chunk
            if bytes_written + chunk_size > size:
                # Last chunk might be smaller
                chunk_size = size - bytes_written
            
            # Generate random bytes
            random_data = os.urandom(chunk_size)
            
            # Write the chunk
            file_obj.write(random_data)
            
            # Flush to disk
            file_obj.flush()
            os.fsync(file_obj.fileno())
            
            bytes_written += chunk_size
    
    def _write_pattern(self, file_obj, pattern, size):
        """
        Write a repeating pattern to a file.
        
        Args:
            file_obj: File object to write to
            pattern: Byte pattern to repeat
            size: Size of the file in bytes
        """
        # Create a chunk of the pattern to write
        chunk_size = min(1024 * 1024, size)  # 1 MB chunks or file size if smaller
        
        # Calculate number of repeats needed to fill the chunk size
        repeats = chunk_size // len(pattern) + 1
        chunk = (pattern * repeats)[:chunk_size]
        
        # Write in chunks to handle large files
        bytes_written = 0
        
        while bytes_written < size:
            # Last chunk might be smaller
            if bytes_written + len(chunk) > size:
                chunk = chunk[:size - bytes_written]
            
            # Write the chunk
            file_obj.write(chunk)
            
            # Flush to disk
            file_obj.flush()
            os.fsync(file_obj.fileno())
            
            bytes_written += len(chunk)