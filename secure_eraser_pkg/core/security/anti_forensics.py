"""
Anti-forensic techniques to enhance security of file wiping operations.

This module implements various anti-forensic techniques to make data recovery
more difficult after wiping, including:
- Timestamp randomization
- File attribute manipulation
- Journal cleaning
- Filename randomization before deletion
- Shadow data handling
"""

import os
import random
import stat
import time
import logging
import datetime
import platform
import subprocess
import string
import shutil
from typing import Dict, List, Optional, Tuple, Union, Any

class ForensicCountermeasures:
    """
    Implementation of anti-forensic techniques to enhance SecureEraser security.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the forensic countermeasures system.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger or logging.getLogger(__name__)
        self._is_windows = platform.system() == "Windows"
        self._is_linux = platform.system() == "Linux"
        self._is_macos = platform.system() == "Darwin"
        self._initialization_time = time.time()
        
        # Track operations for optional cleanup
        self._operations = []
    
    def randomize_timestamps(self, 
                           file_path: str, 
                           min_time: Optional[float] = None,
                           max_time: Optional[float] = None) -> bool:
        """
        Randomize file timestamps to obfuscate when the file was last accessed.
        
        Args:
            file_path: Path to the file
            min_time: Minimum timestamp (as time.time() value)
            max_time: Maximum timestamp (as time.time() value)
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} not found")
            return False
            
        try:
            # Default time range: 1 month ago to current time
            if min_time is None:
                min_time = time.time() - (30 * 24 * 60 * 60)  # 30 days ago
                
            if max_time is None:
                max_time = time.time()
                
            # Generate random access and modification times
            random_atime = random.uniform(min_time, max_time)
            random_mtime = random.uniform(min_time, max_time)
            
            # Apply the timestamps
            os.utime(file_path, (random_atime, random_mtime))
            
            # Log operation for potential cleanup
            self._operations.append({
                "type": "timestamp_randomization",
                "path": file_path,
                "time": time.time()
            })
            
            self.logger.debug(f"Randomized timestamps for {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error randomizing timestamps for {file_path}: {e}")
            return False
    
    def randomize_file_attributes(self, file_path: str) -> bool:
        """
        Randomize file attributes to confuse forensic analysis.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} not found")
            return False
            
        try:
            if self._is_windows:
                # Windows: Use attrib command
                try:
                    attributes = []
                    # Randomly apply attributes
                    for attr, name in [('A', 'archive'), ('H', 'hidden'), ('R', 'readonly'), ('S', 'system')]:
                        if random.choice([True, False]):
                            attributes.append(f"+{attr}")
                            
                    if attributes:
                        cmd = ["attrib"] + attributes + [file_path]
                        subprocess.run(cmd, check=True, capture_output=True)
                        self.logger.debug(f"Set Windows attributes for {file_path}: {attributes}")
                except Exception as e:
                    self.logger.warning(f"Could not set Windows attributes: {e}")
                    
            else:  # Linux/macOS
                # Get current mode
                current_mode = os.stat(file_path).st_mode
                
                # Randomly modify permissions while keeping basic access
                new_mode = current_mode
                
                # Randomly toggle some permission bits
                for bit in [stat.S_IXUSR, stat.S_IXGRP, stat.S_IXOTH]:
                    if random.choice([True, False]):
                        new_mode |= bit  # Set bit
                    else:
                        new_mode &= ~bit  # Clear bit
                
                # Apply new mode
                os.chmod(file_path, new_mode)
            
            # Log operation for potential cleanup
            self._operations.append({
                "type": "attribute_randomization",
                "path": file_path,
                "time": time.time()
            })
            
            self.logger.debug(f"Randomized attributes for {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error randomizing attributes for {file_path}: {e}")
            return False
    
    def rename_with_random_name(self, file_path: str) -> Optional[str]:
        """
        Rename file with random name before deletion to obscure original filename.
        
        Args:
            file_path: Path to the file
            
        Returns:
            New file path if successful, None otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} not found")
            return None
            
        try:
            # Generate random filename
            dir_path = os.path.dirname(file_path)
            file_ext = os.path.splitext(file_path)[1]
            
            # Create random name (10-20 random characters)
            name_length = random.randint(10, 20)
            random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=name_length))
            
            # Create new path
            new_path = os.path.join(dir_path, random_name + file_ext)
            
            # Rename file
            os.rename(file_path, new_path)
            
            # Log operation for potential cleanup
            self._operations.append({
                "type": "file_rename",
                "original_path": file_path,
                "new_path": new_path,
                "time": time.time()
            })
            
            self.logger.debug(f"Renamed {file_path} to {new_path}")
            return new_path
            
        except Exception as e:
            self.logger.error(f"Error renaming {file_path}: {e}")
            return None
    
    def clean_journal_references(self, path: str) -> bool:
        """
        Attempt to clean journal references to the file.
        Note: This requires elevated privileges on most systems.
        
        Args:
            path: File path to clean from journals
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self._is_linux:
                # Linux: Try to clean journal
                filesystem = self._get_filesystem(path)
                
                if 'ext' in filesystem:
                    # For ext2/3/4 filesystems
                    try:
                        # This requires root privileges
                        if os.geteuid() == 0:
                            mount_point = self._get_mount_point(path)
                            if mount_point:
                                cmd = ["tune2fs", "-O", "^has_journal", mount_point]
                                result = subprocess.run(cmd, check=False, capture_output=True)
                                
                                if result.returncode == 0:
                                    self.logger.info(f"Disabled journal on {mount_point}")
                                    
                                    # Re-enable journal after a short delay
                                    time.sleep(1)
                                    cmd = ["tune2fs", "-O", "has_journal", mount_point]
                                    subprocess.run(cmd, check=False, capture_output=True)
                                    
                                    self.logger.info(f"Re-enabled journal on {mount_point}")
                                    return True
                                else:
                                    self.logger.warning(f"Could not modify journal: {result.stderr.decode()}")
                    except Exception as e:
                        self.logger.warning(f"Error manipulating journal: {e}")
                        
            elif self._is_macos:
                # macOS: Attempt to flush logs related to the file
                try:
                    if os.geteuid() == 0:
                        # Flush system logs
                        subprocess.run(["log", "erase", "--all"], check=False, capture_output=True)
                        self.logger.info("Flushed system logs")
                        return True
                except Exception as e:
                    self.logger.warning(f"Could not flush logs: {e}")
                    
            elif self._is_windows:
                # Windows: Limited journal cleaning
                try:
                    # Flush filesystem cache
                    # This doesn't clean the journal but might help
                    if os.path.isfile(path):
                        # Force a sync
                        dir_path = os.path.dirname(path)
                        fsutil_path = shutil.which("fsutil")
                        if fsutil_path:
                            subprocess.run([fsutil_path, "flush", "volume", dir_path], 
                                          check=False, capture_output=True)
                            self.logger.debug(f"Flushed volume containing {path}")
                            return True
                except Exception as e:
                    self.logger.warning(f"Could not flush filesystem cache: {e}")
            
            self.logger.debug(f"Journal cleaning not supported or not privileged on this system")
            return False
            
        except Exception as e:
            self.logger.error(f"Error cleaning journal references: {e}")
            return False
    
    def _get_filesystem(self, path: str) -> str:
        """
        Get filesystem type for a path.
        
        Args:
            path: File path
            
        Returns:
            Filesystem type string
        """
        if self._is_linux:
            try:
                # Use df to get device
                df_result = subprocess.run(["df", "--output=source", path], 
                                          check=True, capture_output=True, text=True)
                device = df_result.stdout.strip().split("\n")[-1]
                
                # Use findmnt to get filesystem type
                findmnt_result = subprocess.run(["findmnt", "-n", "-o", "FSTYPE", device],
                                              check=True, capture_output=True, text=True)
                return findmnt_result.stdout.strip()
            except Exception:
                return "unknown"
                
        elif self._is_macos:
            try:
                # Use mount to get filesystem type
                mount_result = subprocess.run(["mount"], 
                                           check=True, capture_output=True, text=True)
                
                for line in mount_result.stdout.strip().split("\n"):
                    fields = line.split(" ")
                    if len(fields) >= 5:
                        mount_point = fields[2]
                        if path.startswith(mount_point):
                            fs_type = fields[4].strip("()")
                            return fs_type
                            
                return "unknown"
            except Exception:
                return "unknown"
                
        else:  # Windows
            return "ntfs"  # Assume NTFS on Windows
    
    def _get_mount_point(self, path: str) -> Optional[str]:
        """
        Get the mount point for a path.
        
        Args:
            path: File path
            
        Returns:
            Mount point string or None
        """
        if self._is_linux:
            try:
                # Use df to get device
                df_result = subprocess.run(["df", "--output=source", path], 
                                          check=True, capture_output=True, text=True)
                return df_result.stdout.strip().split("\n")[-1]
            except Exception:
                return None
                
        elif self._is_macos:
            try:
                # Use mount to get mount point
                mount_result = subprocess.run(["mount"], 
                                           check=True, capture_output=True, text=True)
                
                longest_match = ""
                longest_mount = None
                
                for line in mount_result.stdout.strip().split("\n"):
                    fields = line.split(" ")
                    if len(fields) >= 3:
                        mount_point = fields[2]
                        if path.startswith(mount_point) and len(mount_point) > len(longest_match):
                            longest_match = mount_point
                            longest_mount = fields[0]
                            
                return longest_mount
            except Exception:
                return None
                
        else:  # Windows
            return None
    
    def manipulate_slack_space(self, file_path: str) -> bool:
        """
        Manipulate file slack space to prevent data recovery.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.logger.error(f"File {file_path} not found or not a file")
            return False
            
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Open file in append mode
            with open(file_path, "ab") as f:
                # Add some random data (1-4KB)
                padding_size = random.randint(1024, 4096)
                padding = bytes(random.getrandbits(8) for _ in range(padding_size))
                f.write(padding)
                
                # Force flush to disk
                f.flush()
                os.fsync(f.fileno())
            
            # Truncate back to original size
            with open(file_path, "ab") as f:
                f.truncate(file_size)
                f.flush()
                os.fsync(f.fileno())
                
            self.logger.debug(f"Manipulated slack space for {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error manipulating slack space: {e}")
            return False
    
    def apply_all_countermeasures(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Apply all anti-forensic countermeasures to a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (success, new_path)
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} not found")
            return (False, None)
            
        try:
            success = True
            current_path = file_path
            
            # 1. Randomize timestamps
            if not self.randomize_timestamps(current_path):
                self.logger.warning(f"Failed to randomize timestamps for {current_path}")
                success = False
                
            # 2. Randomize file attributes
            if not self.randomize_file_attributes(current_path):
                self.logger.warning(f"Failed to randomize attributes for {current_path}")
                success = False
                
            # 3. Manipulate slack space
            if not self.manipulate_slack_space(current_path):
                self.logger.warning(f"Failed to manipulate slack space for {current_path}")
                success = False
                
            # 4. Clean journal references
            self.clean_journal_references(current_path)
            
            # 5. Rename with random name
            new_path = self.rename_with_random_name(current_path)
            if new_path is None:
                self.logger.warning(f"Failed to rename {current_path}")
                success = False
                new_path = current_path
                
            return (success, new_path)
            
        except Exception as e:
            self.logger.error(f"Error applying countermeasures to {file_path}: {e}")
            return (False, None)
    
    def hide_execution_traces(self) -> bool:
        """
        Hide traces of the secure eraser's execution from the system.
        This might include cleaning temporary files, logs, and history.
        
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        try:
            # Clean shell history if possible
            if self._is_linux or self._is_macos:
                history_files = [
                    os.path.expanduser("~/.bash_history"),
                    os.path.expanduser("~/.zsh_history"),
                    os.path.expanduser("~/.history")
                ]
                
                for history_file in history_files:
                    if os.path.exists(history_file):
                        try:
                            # Truncate to zero or clear sensitive commands
                            with open(history_file, "r+") as f:
                                lines = f.readlines()
                                f.seek(0)
                                f.truncate()
                                
                                for line in lines:
                                    # Skip lines containing our program name or secure delete keywords
                                    if "secure_eraser" not in line.lower() and "wipe" not in line.lower():
                                        f.write(line)
                                
                            self.logger.debug(f"Cleaned history file: {history_file}")
                        except Exception as e:
                            self.logger.warning(f"Could not clean history file {history_file}: {e}")
                            success = False
            
            # Clean temp files
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tmp")
            if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                try:
                    for filename in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    self.logger.debug(f"Cleaned temporary files")
                except Exception as e:
                    self.logger.warning(f"Could not clean temporary files: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error hiding execution traces: {e}")
            return False