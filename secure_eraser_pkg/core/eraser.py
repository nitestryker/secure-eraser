"""
Core file and directory erasure functionality.
"""

import os
import random
import sys
import time
import concurrent.futures
import shutil
import datetime
import logging
import math
from typing import Dict, List, Optional, Tuple, Union

from secure_eraser_pkg.utils.patterns import WipePatterns


class SecureEraser:
    """
    Core secure deletion implementation that can:
    1. Securely delete individual files
    2. Wipe free space to prevent recovery of previously deleted files
    3. Securely delete entire directories
    4. Wipe entire drives for resale preparation
    """
    
    def __init__(self, passes: int = 3, method: str = "standard", 
                 verify: bool = False, logger: Optional[logging.Logger] = None):
        """
        Initialize with the number of overwrite passes and wiping method.
        
        Args:
            passes: Number of overwrite passes (higher = more secure but slower)
            method: Wiping method - "standard", "dod", "gutmann", or "paranoid"
                - standard: Uses basic random data (passes parameter determines count)
                - dod: Uses DoD 5220.22-M standard (7 passes minimum)
                - gutmann: Uses Gutmann 35-pass method
                - paranoid: Combines DoD and Gutmann methods plus additional passes
            verify: Whether to perform verification after wiping
            logger: Logger instance to use (if None, a new one will be created)
        """
        self.method = method.lower()
        self.verify = verify
        self.logger = logger or logging.getLogger(__name__)
        
        # Calculate passes based on method
        self.passes = WipePatterns.calculate_passes_for_method(method, passes)
        
        # Track performance stats
        self.performance_stats = {
            "start_time": None,
            "end_time": None,
            "total_bytes_wiped": 0,
            "pass_durations": []
        }
        
        # Initialize verification data (will be populated if verify=True)
        self.verification_data = {
            "wiped_items": [],
            "timestamp": datetime.datetime.now().isoformat(),
            "wiping_method": self.method,
            "passes": self.passes,
            "verification_enabled": self.verify
        }
    
    def secure_delete_file(self, file_path: str) -> bool:
        """
        Securely delete a single file by overwriting it multiple times before deletion.
        Uses the specified wiping method (standard, DoD, Gutmann, or paranoid).
        Optionally computes cryptographic hashes for verification.
        
        Args:
            file_path: Path to the file to securely delete
            
        Returns:
            True if the file was successfully wiped, False otherwise
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.logger.error(f"File {file_path} does not exist or is not a file.")
            return False
            
        try:
            # Get file size and name
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Skip empty files
            if file_size == 0:
                os.remove(file_path)
                self.logger.info(f"Empty file {file_name} removed.")
                
                # Create verification record if verify is enabled
                if self.verify and hasattr(self, 'create_verification_record'):
                    record = self.create_verification_record(
                        file_path=file_path,
                        status="removed (empty file)",
                        before_hashes={},
                        after_hashes={}
                    )
                    self.verification_data["wiped_items"].append(record)
                    
                return True
                
            self.logger.info(f"Securely wiping {file_name} ({file_size/1024/1024:.2f} MB) with {self.passes} passes")
            
            # Compute hashes before wiping for verification
            before_hashes = {}
            if self.verify and hasattr(self, 'compute_file_hash'):
                self.logger.info(f"Computing hashes before wiping")
                before_hashes = self.compute_file_hash(file_path)
            
            # Record start time for performance tracking
            self.performance_stats["start_time"] = datetime.datetime.now()
            
            # For large files, use a chunked approach with progress reporting
            chunk_size = 1024 * 1024 * 10  # 10MB chunks
            
            # Multiple overwrite passes
            for i in range(self.passes):
                pass_start_time = time.time()
                
                # Get pattern name for this pass based on method and pass number
                pattern_name = WipePatterns.get_pattern_name(self.method, i)
                self.logger.info(f"Pass {i+1}/{self.passes}: Writing {pattern_name}")
                
                # Get pattern for this pass
                pattern = WipePatterns.get_pattern_for_pass(self.method, i)
                
                chunks_total = max(1, (file_size + chunk_size - 1) // chunk_size)
                chunks_done = 0
                last_percent = -1
                
                try:
                    with open(file_path, 'wb') as f:
                        remaining_size = file_size
                        
                        while remaining_size > 0:
                            # Determine chunk size for last chunk
                            current_chunk = min(chunk_size, remaining_size)
                            
                            # Generate appropriate data for this pass
                            if pattern:
                                # Use the predefined pattern
                                data = WipePatterns.generate_pattern_data(pattern, current_chunk)
                            else:
                                # Generate random data for this chunk
                                data = bytes(random.getrandbits(8) for _ in range(current_chunk))
                            
                            # Write the chunk
                            f.write(data)
                            
                            # Update progress
                            remaining_size -= current_chunk
                            chunks_done += 1
                            percent = int((chunks_done / chunks_total) * 100)
                            
                            # Only update display when percent changes
                            if percent != last_percent:
                                progress_bar = "#" * (percent // 2) + " " * (50 - (percent // 2))
                                print(f"Progress: [{progress_bar}] {percent}%", end="\r")
                                last_percent = percent
                                
                                # Flush stdout for real-time updates
                                sys.stdout.flush()
                        
                        # Ensure data is written to disk before closing the file
                        f.flush()
                        os.fsync(f.fileno())
                        
                    print()  # New line after progress bar
                    
                    # Record pass duration
                    pass_duration = time.time() - pass_start_time
                    self.performance_stats["pass_durations"].append(pass_duration)
                    
                except Exception as e:
                    self.logger.error(f"Error during pass {i+1}: {e}")
                    raise
                    
            # Record performance statistics
            self.performance_stats["end_time"] = datetime.datetime.now()
            self.performance_stats["total_bytes_wiped"] += file_size
            
            # Compute hashes after wiping for verification
            after_hashes = {}
            if self.verify and hasattr(self, 'compute_file_hash'):
                self.logger.info("Computing hashes after wiping for verification...")
                after_hashes = self.compute_file_hash(file_path)
                
                # Create verification record
                if hasattr(self, 'create_verification_record'):
                    record = self.create_verification_record(
                        file_path=file_path,
                        status="wiped",
                        before_hashes=before_hashes,
                        after_hashes=after_hashes,
                        size=file_size
                    )
                    self.verification_data["wiped_items"].append(record)
                    
                    # Log verification result
                    if record["verification"]["verified"]:
                        self.logger.info("✓ Cryptographic verification: SUCCESSFUL")
                    else:
                        self.logger.warning("⚠ Cryptographic verification: FAILED")
            
            # Finally delete the file
            os.remove(file_path)
            self.logger.info(f"File {file_name} has been securely wiped.")
            return True
        
        except Exception as e:
            self.logger.error(f"Error wiping file {file_path}: {e}")
            return False
    
    def secure_delete_directory(self, directory_path: str) -> bool:
        """
        Securely delete an entire directory and its contents.
        
        Args:
            directory_path: Path to the directory to securely delete
            
        Returns:
            True if the directory was successfully wiped, False otherwise
        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            self.logger.error(f"Directory {directory_path} does not exist or is not a directory.")
            return False
        
        try:
            total_files = 0
            deleted_files = 0
            
            # Walk through the directory and delete all files securely
            for root, dirs, files in os.walk(directory_path, topdown=False):
                for file in files:
                    total_files += 1
                    file_path = os.path.join(root, file)
                    if self.secure_delete_file(file_path):
                        deleted_files += 1
                
                # Remove empty directories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if os.path.exists(dir_path):
                        os.rmdir(dir_path)
            
            # Remove the top directory
            os.rmdir(directory_path)
            self.logger.info(f"Directory {directory_path} has been securely wiped.")
            self.logger.info(f"Total files: {total_files}, Successfully wiped: {deleted_files}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error wiping directory {directory_path}: {e}")
            return False
    
    def wipe_free_space(self, drive_path: str) -> bool:
        """
        Wipe free space to prevent recovery of previously deleted files.
        This is the most important function for ensuring already deleted files can't be recovered.
        Uses multi-threading for improved performance.
        
        Args:
            drive_path: Path to the drive to wipe free space on
            
        Returns:
            True if free space was successfully wiped, False otherwise
        """
        start_time = datetime.datetime.now()
        wiping_stats = {
            "drive_path": drive_path,
            "method": self.method,
            "passes": self.passes,
            "start_time": start_time.isoformat(),
            "bytes_written": 0,
            "verification_result": None
        }
        
        self.logger.info(f"Wiping free space on {drive_path}...")
        self.logger.info(f"Method: {self.method.upper()} with {self.passes} passes")
        
        # Get available free space to estimate progress
        try:
            st = os.statvfs(drive_path)
            total_free_space = st.f_bavail * st.f_frsize
        except Exception as e:
            self.logger.error(f"Could not determine free space on {drive_path}: {e}")
            return False
        
        self.logger.info(f"Detected {total_free_space / (1024**3):.2f} GB of free space to wipe")
        wiping_stats["total_free_space"] = total_free_space
        
        # Create a temporary directory on the specified drive
        temp_dir = os.path.join(drive_path, "temp_secure_wipe")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Determine number of files to create for multi-threading
        # Use one file per thread, with a default of 4 threads, but not more than 8
        num_cpu = min(8, os.cpu_count() or 4)
        num_files = max(1, num_cpu - 1)  # Leave one CPU core free
        self.logger.info(f"Using {num_files} parallel threads for wiping")
        
        # Size of each chunk to write at once (10MB)
        chunk_size = 1024 * 1024 * 10
        
        try:
            # For each pass
            for current_pass in range(self.passes):
                # Get pattern based on method and current pass
                pattern = WipePatterns.get_pattern_for_pass(self.method, current_pass)
                pattern_name = WipePatterns.get_pattern_name(self.method, current_pass)
                
                self.logger.info(f"\nPass {current_pass+1}/{self.passes}: Writing {pattern_name}")
                bytes_written = 0
                last_percent = 0
                
                # Create pattern data for this chunk based on the pattern
                pattern_data = WipePatterns.generate_pattern_data(pattern, chunk_size)
                
                # Create multiple files and write to them in parallel
                file_paths = [os.path.join(temp_dir, f"wipe_file_{i}") for i in range(num_files)]
                
                # Function for thread to fill a file until disk is full
                def fill_file(file_path):
                    try:
                        with open(file_path, 'wb') as f:
                            while True:
                                f.write(pattern_data)
                                f.flush()
                                os.fsync(f.fileno())
                    except IOError:
                        # Expected when disk gets full
                        return
                
                # Initial progress bar
                print("Progress: [" + " " * 50 + "] 0%", end="\r")
                sys.stdout.flush()
                
                # Start the threads
                with concurrent.futures.ThreadPoolExecutor(max_workers=num_files) as executor:
                    # Submit the file filling tasks
                    futures = [executor.submit(fill_file, fp) for fp in file_paths]
                    
                    # While files are being filled, monitor progress
                    while not all(future.done() for future in futures):
                        # Calculate bytes written by checking file sizes
                        current_bytes = sum(os.path.getsize(fp) for fp in file_paths if os.path.exists(fp))
                        if current_bytes > bytes_written:
                            bytes_written = current_bytes
                            percent = min(100, int((bytes_written / total_free_space) * 100))
                            
                            # Update progress bar
                            if percent > last_percent:
                                progress_bar = "#" * (percent // 2) + " " * (50 - (percent // 2))
                                print(f"Progress: [{progress_bar}] {percent}%", end="\r")
                                last_percent = percent
                                sys.stdout.flush()
                        
                        # Small sleep to prevent CPU hogging
                        time.sleep(0.1)
                
                # Record bytes written for this pass
                wiping_stats["bytes_written"] += bytes_written
                self.logger.info(f"\nPass {current_pass+1}/{self.passes} complete - {bytes_written / (1024**3):.2f} GB written")
                
                # Delete the files before next pass
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            self.logger.info("\nWiping complete. Running verification...")
            
            # Verification pass - check if free space contains our pattern
            verification_result = self._verify_wiping(drive_path, temp_dir)
            wiping_stats["verification_result"] = verification_result
            
            # Final cleanup
            self.logger.info("Final cleanup - removing temporary files")
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Record end time
            end_time = datetime.datetime.now()
            wiping_stats["end_time"] = end_time.isoformat()
            wiping_stats["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Complete! Free space on {drive_path} has been wiped with {self.passes} passes using {self.method.upper()} method.")
            self.logger.info(f"Duration: {str(end_time - start_time).split('.')[0]}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"\nError wiping free space on {drive_path}: {e}")
            # Clean up in case of error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return False
            
    def _verify_wiping(self, drive_path: str, temp_dir: str) -> Dict:
        """
        Verify the wiping was effective by checking if random samples of free space
        contain non-wiped data.
        
        Args:
            drive_path: Path to the drive
            temp_dir: Temporary directory on the drive to use for verification
            
        Returns:
            Dictionary with verification results
        """
        self.logger.info("Performing verification by sampling free space...")
        verification_results = {
            "samples_checked": 0,
            "suspicious_samples": 0,
            "verification_passed": True,
            "sample_results": []
        }
        
        # Create a verification file to sample free space
        verify_file_path = os.path.join(temp_dir, "verify_wipe")
        verify_size = 1024 * 1024 * 100  # 100MB verification sample
        
        try:
            # Create a large file to capture some free space
            with open(verify_file_path, 'wb') as f:
                f.write(b'\x00' * verify_size)
                f.flush()
                os.fsync(f.fileno())
            
            # Now read it and check for patterns that might indicate data wasn't wiped
            with open(verify_file_path, 'rb') as f:
                # Check multiple samples within the file
                num_samples = 20
                sample_size = 4096  # 4KB sample size
                
                for i in range(num_samples):
                    # Seek to a random position in the file
                    pos = random.randint(0, max(0, verify_size - sample_size))
                    f.seek(pos)
                    
                    # Read a sample
                    sample = f.read(sample_size)
                    verification_results["samples_checked"] += 1
                    
                    # Check if sample contains suspicious data
                    # Simple heuristic: consider the sample suspicious if it has very high entropy
                    # or contains recognizable patterns
                    if self._is_suspicious_sample(sample):
                        verification_results["suspicious_samples"] += 1
                        verification_results["sample_results"].append({
                            "offset": pos,
                            "suspicious": True,
                            "entropy": self._calculate_entropy(sample),
                            "sample_hex": sample[:32].hex()  # Include first 32 bytes as hex
                        })
                    else:
                        verification_results["sample_results"].append({
                            "offset": pos,
                            "suspicious": False,
                            "entropy": self._calculate_entropy(sample)
                        })
            
            # Clean up verification file
            os.remove(verify_file_path)
            
            # If more than 5% of samples are suspicious, consider verification failed
            if verification_results["suspicious_samples"] / verification_results["samples_checked"] > 0.05:
                verification_results["verification_passed"] = False
                self.logger.warning(f"⚠ Verification found {verification_results['suspicious_samples']} suspicious samples out of {verification_results['samples_checked']}")
            else:
                self.logger.info(f"✓ Verification passed: {verification_results['suspicious_samples']} suspicious samples out of {verification_results['samples_checked']}")
                
            return verification_results
            
        except Exception as e:
            self.logger.error(f"Error during verification: {e}")
            verification_results["error"] = str(e)
            verification_results["verification_passed"] = False
            return verification_results
            
    def _is_suspicious_sample(self, sample: bytes) -> bool:
        """
        Check if a sample contains data that seems suspicious 
        (not random, not zeros, possible file fragments).
        
        Args:
            sample: Bytes to check
            
        Returns:
            True if sample seems suspicious, False otherwise
        """
        # Check if sample is all zeros or all ones (expected after wiping)
        if sample == b'\x00' * len(sample) or sample == b'\xFF' * len(sample):
            return False
            
        # Check if sample has very low entropy (likely wiped with a pattern)
        entropy = self._calculate_entropy(sample)
        if entropy < 0.5:
            return False
            
        # Check for common file signatures
        signatures = [
            b'PK\x03\x04',      # ZIP
            b'\x25\x50\x44\x46', # PDF
            b'\xFF\xD8\xFF',     # JPEG
            b'GIF',              # GIF
            b'\x89PNG',          # PNG
            b'BM',               # BMP
            b'\x00\x00\x01\xB3', # MPEG
            b'ID3',              # MP3
            b'\x00\x01\x00\x00', # TrueType font
            b'<!DOCTYPE',        # HTML
            b'<html',            # HTML
            b'<?xml',            # XML
            b'-----BEGIN',       # PEM
            b'{\r\n',            # JSON
            b'{\n',              # JSON
            b'SQLite',           # SQLite
            b'FROM ',            # SQL
            b'SELECT ',          # SQL
            b'CREATE ',          # SQL
            b'#include',         # C/C++
            b'import ',          # Python/Java
            b'public class',     # Java
            b'private ',         # Various
            b'function ',        # JavaScript
            b'def ',             # Python
            b'class ',           # Various
        ]
        
        for sig in signatures:
            if sig in sample:
                return True
                
        # If entropy is very high, it might be encrypted data or compressed files
        if entropy > 0.95:
            return True
            
        # Default to not suspicious
        return False
            
    def _calculate_entropy(self, data: bytes) -> float:
        """
        Calculate the Shannon entropy of data (measure of randomness).
        
        Args:
            data: Bytes to calculate entropy for
            
        Returns:
            Entropy value between 0 and 1
        """
        if not data:
            return 0
            
        # Count occurrences of each byte value
        counts = {}
        for byte in data:
            counts[byte] = counts.get(byte, 0) + 1
            
        # Calculate entropy
        entropy = 0
        for count in counts.values():
            probability = count / len(data)
            entropy -= probability * math.log2(probability)
            
        # Normalize to [0, 1]
        return entropy / 8  # 8 bits per byte = maximum possible entropy
            
    def wipe_entire_drive(self, drive_path: str, force: bool = False) -> bool:
        """
        Wipe an entire drive, including all files, directories, and free space.
        Extremely destructive - requires force=True to run.
        
        Args:
            drive_path: Path to the drive to wipe
            force: Set to True to confirm destructive operation
            
        Returns:
            True if the drive was successfully wiped, False otherwise
        """
        if not force:
            self.logger.error("Wiping an entire drive requires the 'force' parameter to be set to True. This is an extremely destructive operation.")
            return False
            
        if not os.path.exists(drive_path) or not os.path.isdir(drive_path):
            self.logger.error(f"Drive path {drive_path} does not exist or is not accessible.")
            return False
            
        try:
            self.logger.warning(f"!!! WIPING ENTIRE DRIVE {drive_path} !!!")
            self.logger.warning("This will permanently delete ALL data on the drive.")
            self.logger.warning(f"Using method: {self.method.upper()} with {self.passes} passes")
            
            # First, delete all files and directories
            self.logger.info("Step 1: Wiping all files and directories...")
            
            deleted_files = 0
            deleted_dirs = 0
            
            for root, dirs, files in os.walk(drive_path, topdown=False):
                # Skip the root directory itself
                if root == drive_path:
                    continue
                    
                # Delete all files in this directory
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if self.secure_delete_file(file_path):
                            deleted_files += 1
                    except Exception as e:
                        self.logger.error(f"Error deleting file {file_path}: {e}")
                
                # Delete all subdirectories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if os.path.exists(dir_path):
                            os.rmdir(dir_path)
                            deleted_dirs += 1
                    except Exception as e:
                        self.logger.error(f"Error removing directory {dir_path}: {e}")
            
            self.logger.info(f"Deleted {deleted_files} files and {deleted_dirs} directories.")
            
            # Next, wipe free space
            self.logger.info("Step 2: Wiping free space...")
            self.wipe_free_space(drive_path)
            
            self.logger.info(f"Drive {drive_path} has been securely wiped.")
            return True
            
        except Exception as e:
            self.logger.error(f"Error wiping drive {drive_path}: {e}")
            return False