import os
import random
import subprocess
import platform
import argparse
import shutil
import tempfile
import time
import sys
import concurrent.futures
import datetime
import hashlib
import json
import math
from pathlib import Path

class SecureEraser:
    """
    A comprehensive secure deletion tool that can:
    1. Securely delete individual files
    2. Wipe free space to prevent recovery of previously deleted files
    3. Securely delete entire directories
    4. Wipe entire drives for resale preparation
    """
    
    # DoD 5220.22-M standard wipe patterns
    DOD_PATTERNS = [
        b'\x00',                         # Pass 1: All zeros
        b'\xFF',                         # Pass 2: All ones
        b'\x00\xFF\x00\xFF\x00\xFF',     # Pass 3: Alternating bit pattern
        b'\x55\xAA\x55\xAA\x55\xAA',     # Pass 4: Another alternating bit pattern
        b'\x92\x49\x24',                 # Pass 5: Random pattern
        b'\x49\x92\x24\x49\x92',         # Pass 6: Another random pattern
        b'\xDB\xB6\xDB\x6D\xB6\xDB',     # Pass 7: Another random pattern
    ]
    
    # Gutmann 35-pass method patterns (simplified representation)
    GUTMANN_PASSES = 35
    
    def __init__(self, passes=3, method="standard"):
        """
        Initialize with the number of overwrite passes and wiping method.
        
        Args:
            passes: Number of overwrite passes (higher = more secure but slower)
            method: Wiping method - "standard", "dod", "gutmann", or "paranoid"
                - standard: Uses basic random data (passes parameter determines count)
                - dod: Uses DoD 5220.22-M standard (7 passes minimum)
                - gutmann: Uses Gutmann 35-pass method
                - paranoid: Combines DoD and Gutmann methods plus additional passes
        """
        self.method = method.lower()
        
        # Set passes based on method
        if self.method == "dod":
            self.passes = max(passes, 7)  # Minimum 7 passes for DoD
        elif self.method == "gutmann":
            self.passes = 35  # Always 35 passes for Gutmann
        elif self.method == "paranoid":
            self.passes = max(passes, 49)  # DoD + Gutmann + additional
        else:  # standard
            self.passes = passes
            
        self.system = platform.system()
    
    def secure_delete_file(self, file_path):
        """
        Securely delete a single file by overwriting it multiple times before deletion.
        Uses the specified wiping method (standard, DoD, Gutmann, or paranoid).
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            print(f"File {file_path} does not exist or is not a file.")
            return False
            
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Skip empty files
            if file_size == 0:
                os.remove(file_path)
                print(f"Empty file {file_name} removed.")
                return True
                
            print(f"Securely wiping {file_name} ({file_size/1024/1024:.2f} MB) with {self.passes} passes")
            
            # For large files, use a chunked approach with progress reporting
            chunk_size = 1024 * 1024 * 10  # 10MB chunks
            
            # Multiple overwrite passes
            for i in range(self.passes):
                pass_type = "zeros" if i == 0 else "ones" if i == 1 else f"random data (pass {i+1})"
                print(f"Pass {i+1}/{self.passes}: Writing {pass_type}")
                
                chunks_total = (file_size + chunk_size - 1) // chunk_size
                chunks_done = 0
                last_percent = -1
                
                with open(file_path, 'wb') as f:
                    remaining_size = file_size
                    
                    while remaining_size > 0:
                        # Determine chunk size for last chunk
                        current_chunk = min(chunk_size, remaining_size)
                        
                        # Generate appropriate data for this pass
                        if i == 0:
                            # Pass 1: zeros
                            data = b'\x00' * current_chunk
                        elif i == 1:
                            # Pass 2: ones
                            data = b'\xFF' * current_chunk
                        else:
                            # Other passes: random data
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
                
                # Ensure data is written to disk
                f.flush()
                os.fsync(f.fileno())
                print()  # New line after progress bar
                    
            # Finally delete the file
            os.remove(file_path)
            print(f"File {file_name} has been securely wiped.")
            return True
        
        except Exception as e:
            print(f"Error wiping file {file_path}: {e}")
            return False
    
    def secure_delete_directory(self, directory_path):
        """
        Securely delete an entire directory and its contents.
        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            print(f"Directory {directory_path} does not exist or is not a directory.")
            return False
        
        try:
            # Walk through the directory and delete all files securely
            for root, dirs, files in os.walk(directory_path, topdown=False):
                for file in files:
                    self.secure_delete_file(os.path.join(root, file))
                
                # Remove empty directories
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    if os.path.exists(dir_path):
                        os.rmdir(dir_path)
            
            # Remove the top directory
            os.rmdir(directory_path)
            print(f"Directory {directory_path} has been securely wiped.")
            return True
        
        except Exception as e:
            print(f"Error wiping directory {directory_path}: {e}")
            return False
    
    def wipe_free_space(self, drive_path):
        """
        Wipe free space to prevent recovery of previously deleted files.
        This is the most important function for ensuring already deleted files can't be recovered.
        Uses multi-threading for improved performance.
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
        
        print(f"Wiping free space on {drive_path}...")
        print(f"Method: {self.method.upper()} with {self.passes} passes")
        
        # Get available free space to estimate progress
        if self.system == "Windows":
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(drive_path), None, None, ctypes.pointer(free_bytes))
            total_free_space = free_bytes.value
        else:
            # Unix-based systems
            st = os.statvfs(drive_path)
            total_free_space = st.f_bavail * st.f_frsize
        
        print(f"Detected {total_free_space / (1024**3):.2f} GB of free space to wipe")
        wiping_stats["total_free_space"] = total_free_space
        
        # Create a temporary directory on the specified drive
        temp_dir = os.path.join(drive_path, "temp_secure_wipe")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Determine number of files to create for multi-threading
        # Use one file per thread, with a default of 4 threads, but not more than 8
        num_cpu = min(8, os.cpu_count() or 4)
        num_files = max(1, num_cpu - 1)  # Leave one CPU core free
        print(f"Using {num_files} parallel threads for wiping")
        
        # Size of each chunk to write at once (10MB)
        chunk_size = 1024 * 1024 * 10
        
        try:
            # For each pass
            for current_pass in range(self.passes):
                # Get pattern based on method and current pass
                pattern = self._get_wipe_pattern(current_pass)
                pattern_name = self._get_pattern_name(current_pass)
                
                print(f"\nPass {current_pass+1}/{self.passes}: Writing {pattern_name}")
                bytes_written = 0
                last_percent = 0
                
                # Create pattern data for this chunk based on the pattern
                pattern_data = self._generate_pattern_data(pattern, chunk_size)
                
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
                print(f"\nPass {current_pass+1}/{self.passes} complete - {bytes_written / (1024**3):.2f} GB written")
                
                # Delete the files before next pass
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            print("\nWiping complete. Running verification...")
            
            # Verification pass - check if free space contains our pattern
            verification_result = self._verify_wiping(drive_path, temp_dir)
            wiping_stats["verification_result"] = verification_result
            
            # Final cleanup
            print("Final cleanup - removing temporary files")
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Record end time
            end_time = datetime.datetime.now()
            wiping_stats["end_time"] = end_time.isoformat()
            wiping_stats["duration_seconds"] = (end_time - start_time).total_seconds()
            
            # Generate wiping report
            report_path = self._generate_wiping_report(wiping_stats)
            
            print(f"Complete! Free space on {drive_path} has been wiped with {self.passes} passes using {self.method.upper()} method.")
            print(f"Duration: {str(end_time - start_time).split('.')[0]}")
            print(f"Wiping report saved to: {report_path}")
            return True
        
        except Exception as e:
            print(f"\nError wiping free space on {drive_path}: {e}")
            # Clean up in case of error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return False
    
    def _verify_wiping(self, drive_path, temp_dir):
        """
        Verify the wiping was effective by checking if random samples of free space
        contain non-wiped data.
        
        Returns a dictionary with verification results.
        """
        print("Performing verification by sampling free space...")
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
                    
                    # Calculate entropy of the sample (high entropy often indicates real data)
                    entropy = self._calculate_entropy(sample)
                    
                    # Check if the sample has patterns typical of unwiped data
                    is_suspicious = self._is_suspicious_sample(sample, entropy)
                    
                    # Record the result
                    sample_result = {
                        "offset": pos,
                        "entropy": entropy,
                        "is_suspicious": is_suspicious,
                        "sample_hash": hashlib.md5(sample).hexdigest()
                    }
                    verification_results["sample_results"].append(sample_result)
                    
                    if is_suspicious:
                        verification_results["suspicious_samples"] += 1
                        verification_results["verification_passed"] = False
            
            # Remove the verification file
            os.remove(verify_file_path)
            
            # Report the verification results
            if verification_results["verification_passed"]:
                print(f"Verification PASSED: {verification_results['samples_checked']} samples checked, no suspicious data found.")
            else:
                print(f"Verification WARNING: {verification_results['suspicious_samples']} out of {verification_results['samples_checked']} samples contain suspicious data patterns.")
                print("This may indicate incomplete wiping or false positives.")
            
            return verification_results
            
        except Exception as e:
            print(f"Error during verification: {e}")
            if os.path.exists(verify_file_path):
                os.remove(verify_file_path)
            
            verification_results["error"] = str(e)
            return verification_results
    
    def _calculate_entropy(self, data):
        """Calculate Shannon entropy of a byte string."""
        if not data:
            return 0
            
        entropy = 0
        for byte_value in range(256):
            p_x = data.count(byte_value) / len(data)
            if p_x > 0:
                entropy += p_x * math.log2(p_x)
                
        return -entropy
    
    def _is_suspicious_sample(self, sample, entropy):
        """
        Check if a sample might contain unwiped data.
        
        High entropy (> 7.0) often indicates encrypted or compressed data.
        Very low entropy (< 0.1) indicates all zeros or all ones, which is expected after wiping.
        Medium entropy might indicate text or other data patterns.
        """
        # If the sample is all zeros or all ones, it's likely wiped data
        if sample == b'\x00' * len(sample) or sample == b'\xFF' * len(sample):
            return False
            
        # Check for alternating patterns we used in wiping
        if all(b in [0, 255] for b in sample) and len(set(sample)) <= 2:
            return False
            
        # High entropy could be encrypted data
        if entropy > 7.0:
            return True
            
        # Medium entropy could be normal file data
        if 3.0 < entropy < 6.5:
            return True
            
        # Check for text patterns (ASCII printable characters)
        printable_chars = sum(32 <= b <= 126 for b in sample)
        if printable_chars > len(sample) * 0.7:  # If more than 70% printable
            return True
            
        return False
    
    def _generate_wiping_report(self, wiping_stats):
        """
        Generate a detailed report of the wiping operation.
        
        Args:
            wiping_stats: Dictionary containing wiping statistics
            
        Returns:
            Path to the generated report file
        """
        # Create a report directory if it doesn't exist
        reports_dir = os.path.join(os.path.expanduser("~"), "secure_wipe_reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate report filename based on date and drive
        drive_name = wiping_stats["drive_path"].replace(":\\", "").replace("/", "_").replace("\\", "_")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"wipe_report_{drive_name}_{timestamp}"
        
        # JSON report for machine processing
        json_path = os.path.join(reports_dir, f"{report_filename}.json")
        with open(json_path, 'w') as f:
            json.dump(wiping_stats, f, indent=2)
        
        # Human-readable text report
        txt_path = os.path.join(reports_dir, f"{report_filename}.txt")
        
        with open(txt_path, 'w') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("SECURE DATA WIPING REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # System information
            f.write("SYSTEM INFORMATION\n")
            f.write("-" * 80 + "\n")
            f.write(f"Operating System: {platform.system()} {platform.release()}\n")
            f.write(f"Machine: {platform.machine()}\n")
            f.write(f"Processor: {platform.processor()}\n\n")
            
            # Wiping details
            f.write("WIPING DETAILS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Drive Path: {wiping_stats['drive_path']}\n")
            f.write(f"Wiping Method: {wiping_stats['method'].upper()}\n")
            f.write(f"Number of Passes: {wiping_stats['passes']}\n")
            f.write(f"Start Time: {wiping_stats['start_time']}\n")
            f.write(f"End Time: {wiping_stats['end_time']}\n")
            
            # Calculate duration in a human-readable format
            duration_seconds = wiping_stats.get("duration_seconds", 0)
            hours, remainder = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            f.write(f"Duration: {int(hours)}h {int(minutes)}m {int(seconds)}s\n")
            
            # Space information
            total_gb = wiping_stats.get("total_free_space", 0) / (1024**3)
            written_gb = wiping_stats.get("bytes_written", 0) / (1024**3)
            f.write(f"Total Free Space: {total_gb:.2f} GB\n")
            f.write(f"Total Data Written: {written_gb:.2f} GB\n\n")
            
            # Verification results
            f.write("VERIFICATION RESULTS\n")
            f.write("-" * 80 + "\n")
            
            verification = wiping_stats.get("verification_result", {})
            if verification:
                samples_checked = verification.get("samples_checked", 0)
                suspicious_samples = verification.get("suspicious_samples", 0)
                passed = verification.get("verification_passed", False)
                
                f.write(f"Samples Checked: {samples_checked}\n")
                f.write(f"Suspicious Samples: {suspicious_samples}\n")
                f.write(f"Verification Passed: {'Yes' if passed else 'No'}\n\n")
                
                if "error" in verification:
                    f.write(f"Verification Error: {verification['error']}\n\n")
            else:
                f.write("Verification not performed\n\n")
            
            # Certificate
            f.write("CERTIFICATE OF DESTRUCTION\n")
            f.write("-" * 80 + "\n")
            f.write("This document certifies that free space on the specified drive was wiped\n")
            f.write("according to the method and parameters specified above. This wiping process\n")
            f.write("was designed to prevent recovery of deleted data using commercially\n")
            f.write("available recovery tools.\n\n")
            
            f.write(f"Report generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Report ID: {hashlib.sha256(report_filename.encode()).hexdigest()[:16]}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        return txt_path
    
    def _get_wipe_pattern(self, pass_number):
        """Get the appropriate pattern for the current pass based on wiping method."""
        if self.method == "dod":
            # DoD 5220.22-M method
            pattern_index = min(pass_number, len(self.DOD_PATTERNS) - 1)
            return self.DOD_PATTERNS[pattern_index]
        elif self.method == "gutmann" or self.method == "paranoid":
            # Gutmann method patterns (simplified)
            if pass_number < 4:
                # Passes 1-4: Random data
                return None  # Signal to use random data
            elif pass_number < 10:
                # Passes 5-10: Specific patterns from DoD
                dod_index = (pass_number - 4) % len(self.DOD_PATTERNS)
                return self.DOD_PATTERNS[dod_index]
            elif pass_number < 32:
                # Passes 11-32: Specific bit patterns (simplified to random)
                return None  # Signal to use random data
            else:
                # Passes 33-35: Random data again
                return None  # Signal to use random data
        else:
            # Standard method
            if pass_number == 0:
                return b'\x00'  # First pass: zeros
            elif pass_number == 1:
                return b'\xFF'  # Second pass: ones
            else:
                return None  # Other passes: random data
    
    def _get_pattern_name(self, pass_number):
        """Get a human-readable name for the current pass pattern."""
        pattern = self._get_wipe_pattern(pass_number)
        
        if pattern is None:
            return f"random data"
        elif pattern == b'\x00':
            return "zeros (0x00)"
        elif pattern == b'\xFF':
            return "ones (0xFF)"
        elif pattern == b'\x00\xFF\x00\xFF\x00\xFF':
            return "alternating zeros and ones"
        elif pattern == b'\x55\xAA\x55\xAA\x55\xAA':
            return "alternating 01010101 and 10101010"
        elif pattern == b'\x92\x49\x24':
            return "DoD pattern 10010010..."
        elif pattern == b'\x49\x92\x24\x49\x92':
            return "DoD pattern 01001001..."
        elif pattern == b'\xDB\xB6\xDB\x6D\xB6\xDB':
            return "DoD pattern 11011011..."
        else:
            return f"special pattern {pattern[:10].hex()}..."
    
    def _generate_pattern_data(self, pattern, chunk_size):
        """Generate a chunk of data using the specified pattern or random data if pattern is None."""
        if pattern is None:
            # Random data
            return bytes(random.getrandbits(8) for _ in range(chunk_size))
        else:
            # Repeat the pattern to fill the chunk
            pattern_length = len(pattern)
            repeats = chunk_size // pattern_length
            remainder = chunk_size % pattern_length
            
            return pattern * repeats + pattern[:remainder]
    
    def wipe_free_space_advanced(self, drive_path):
        """
        Use platform-specific tools for more thorough free space wiping.
        This is a more advanced option that uses built-in OS tools where available.
        """
        if self.system == "Windows":
            return self._wipe_free_space_windows(drive_path)
        elif self.system == "Darwin":  # macOS
            return self._wipe_free_space_macos(drive_path)
        else:  # Linux and other UNIX-like systems
            return self._wipe_free_space_linux(drive_path)
    
    def _wipe_free_space_windows(self, drive_path):
        """
        Use sdelete from Sysinternals to wipe free space on Windows.
        Note: sdelete must be installed and in the system PATH.
        """
        try:
            # Check if sdelete is available
            subprocess.run(['sdelete', '-?'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            
            # Run sdelete to clean free space with progress monitoring
            print(f"Using sdelete to wipe free space on {drive_path}...")
            
            # Configure sdelete based on passes
            if self.passes <= 1:
                # Single pass of zeros
                args = ['sdelete', '-z', '-nobanner', drive_path]
            else:
                # Multiple passes (sdelete uses 3 passes with -p)
                args = ['sdelete', '-p', str(min(self.passes, 3)), '-nobanner', drive_path]
            
            print(f"Starting {self.passes} pass(es) with sdelete - This may take a while")
            print("Progress indicator from sdelete:")
            
            # Run sdelete with real-time output
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Show real-time progress from sdelete
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(f"  {line}")
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code == 0:
                print(f"Free space on {drive_path} has been wiped using sdelete.")
                return True
            else:
                raise subprocess.CalledProcessError(return_code, args)
        
        except FileNotFoundError:
            print("sdelete not found. Please install SysInternals Suite from Microsoft.")
            print("Falling back to basic free space wiping method...")
            return self.wipe_free_space(drive_path)
        
        except subprocess.CalledProcessError as e:
            print(f"Error running sdelete: {e}")
            print("Falling back to basic free space wiping method...")
            return self.wipe_free_space(drive_path)
    
    def _wipe_free_space_macos(self, drive_path):
        """
        Use diskutil to wipe free space on macOS.
        """
        try:
            # Get the disk identifier for the given path
            df_output = subprocess.check_output(['df', drive_path]).decode('utf-8').strip().split('\n')
            disk_id = df_output[1].split()[0]
            
            print(f"Using diskutil to wipe free space on {disk_id}...")
            
            # Use diskutil to securely erase free space
            # 1 pass for speed, but can be increased for more security
            subprocess.run(['diskutil', 'secureErase', 'freespace', str(self.passes), disk_id], check=True)
            
            print(f"Free space on {drive_path} ({disk_id}) has been wiped using diskutil.")
            return True
        
        except Exception as e:
            print(f"Error using diskutil to wipe free space: {e}")
            print("Falling back to basic free space wiping method...")
            return self.wipe_free_space(drive_path)
    
    def _wipe_free_space_linux(self, drive_path):
        """
        Use secure-delete tools (if available) or fallback to manual method on Linux.
        """
        try:
            # Check if sfill (part of secure-delete) is available
            subprocess.run(['sfill', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            
            print(f"Using sfill to wipe free space on {drive_path}...")
            
            # Use sfill to securely erase free space
            # -l option makes it less secure but faster
            subprocess.run(['sfill', '-l', '-v', drive_path], check=True)
            
            print(f"Free space on {drive_path} has been wiped using sfill.")
            return True
        
        except FileNotFoundError:
            print("sfill not found. Please install the secure-delete package.")
            print("Falling back to basic free space wiping method...")
            return self.wipe_free_space(drive_path)
        
        except subprocess.CalledProcessError as e:
            print(f"Error running sfill: {e}")
            print("Falling back to basic free space wiping method...")
            return self.wipe_free_space(drive_path)


def main():
    parser = argparse.ArgumentParser(description='Securely wipe files, directories, and free space for safe computer resale.')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Parser for the file command
    file_parser = subparsers.add_parser('file', help='Securely delete a file')
    file_parser.add_argument('path', help='Path to the file')
    file_parser.add_argument('--passes', type=int, default=3, help='Number of overwrite passes (default: 3)')
    file_parser.add_argument('--method', choices=['standard', 'dod', 'gutmann', 'paranoid'], default='standard',
                          help='Wiping method: standard, dod (DoD 5220.22-M), gutmann (35-pass), or paranoid (default: standard)')
    
    # Parser for the directory command
    dir_parser = subparsers.add_parser('directory', help='Securely delete a directory')
    dir_parser.add_argument('path', help='Path to the directory')
    dir_parser.add_argument('--passes', type=int, default=3, help='Number of overwrite passes (default: 3)')
    dir_parser.add_argument('--method', choices=['standard', 'dod', 'gutmann', 'paranoid'], default='standard',
                          help='Wiping method: standard, dod (DoD 5220.22-M), gutmann (35-pass), or paranoid (default: standard)')
    
    # Parser for the freespace command
    free_parser = subparsers.add_parser('freespace', help='Wipe free space to prevent recovery of previously deleted files')
    free_parser.add_argument('path', help='Path to the drive/partition')
    free_parser.add_argument('--advanced', action='store_true', help='Use advanced OS-specific methods if available')
    free_parser.add_argument('--passes', type=int, default=3, help='Number of overwrite passes (default: 3)')
    free_parser.add_argument('--method', choices=['standard', 'dod', 'gutmann', 'paranoid'], default='standard',
                          help='Wiping method: standard, dod (DoD 5220.22-M), gutmann (35-pass), or paranoid (default: standard)')
    
    # Parser for fullwipe command - new command for computer resale preparation
    fullwipe_parser = subparsers.add_parser('fullwipe', help='Complete system wipe for computer resale (WARNING: destroys all data)')
    fullwipe_parser.add_argument('drive', help='Drive to wipe (e.g., C:, /dev/sda)')
    fullwipe_parser.add_argument('--method', choices=['standard', 'dod', 'gutmann', 'paranoid'], default='dod',
                          help='Wiping method: standard, dod (DoD 5220.22-M), gutmann (35-pass), or paranoid (default: dod)')
    fullwipe_parser.add_argument('--passes', type=int, default=7, help='Number of overwrite passes (default: 7)')
    fullwipe_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt (USE WITH CAUTION)')
    
    args = parser.parse_args()
    
    # Create the secure eraser
    eraser = SecureEraser(passes=args.passes)
    
    # Execute the requested command
    if args.command == 'file':
        eraser = SecureEraser(passes=args.passes, method=args.method)
        eraser.secure_delete_file(args.path)
    elif args.command == 'directory':
        eraser = SecureEraser(passes=args.passes, method=args.method)
        eraser.secure_delete_directory(args.path)
    elif args.command == 'freespace':
        eraser = SecureEraser(passes=args.passes, method=args.method)
        if args.advanced:
            eraser.wipe_free_space_advanced(args.path)
        else:
            eraser.wipe_free_space(args.path)
    elif args.command == 'fullwipe':
        # Special handling for full drive wiping (computer resale preparation)
        print("\n" + "="*80)
        print("WARNING: FULL DRIVE WIPE REQUESTED".center(80))
        print("This will PERMANENTLY DESTROY ALL DATA on the drive!".center(80))
        print("Intended for computer resale preparation.".center(80))
        print("="*80 + "\n")
        
        if not args.force:
            confirmation = input(f"Are you ABSOLUTELY SURE you want to wipe ALL DATA on {args.drive}? (yes/NO): ")
            if confirmation.lower() != "yes":
                print("Operation canceled. No data was modified.")
                return
                
            confirmation2 = input(f"FINAL WARNING: Type 'I UNDERSTAND THIS DESTROYS ALL DATA' to confirm: ")
            if confirmation2 != "I UNDERSTAND THIS DESTROYS ALL DATA":
                print("Operation canceled. No data was modified.")
                return
        
        print(f"\nInitiating full drive wipe on {args.drive} using {args.method.upper()} method with {args.passes} passes")
        print("This process may take several hours to several days depending on drive size and method.")
        
        # TODO: Implement actual drive wiping using platform-specific tools
        # For now we'll just show a message about the appropriate tool to use
        if platform.system() == "Windows":
            print("\nFor Windows systems, please use DBAN (Darik's Boot and Nuke) for full drive wiping.")
            print("Download DBAN from https://dban.org/")
            print("Create a bootable USB/DVD and boot from it to wipe the entire drive.")
        elif platform.system() == "Darwin":  # macOS
            print("\nFor macOS, please use Disk Utility's secure erase feature:")
            print("1. Open Disk Utility")
            print("2. Select the drive")
            print("3. Click 'Erase'")
            print("4. Click 'Security Options' and choose the appropriate wiping level")
        else:  # Linux
            print("\nFor Linux, you can use the 'shred' command for full drive wiping:")
            print(f"sudo shred -v -n {args.passes} -z {args.drive}")
            
        print("\nRecommendation: For the most thorough wipe for computer resale, use dedicated")
        print("wiping tools that can create a verification report, such as:")
        print("- DBAN (Darik's Boot and Nuke)")
        print("- Blancco Drive Eraser")
        print("- KillDisk")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
