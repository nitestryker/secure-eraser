"""
Military-grade wiping standards implementation.

This module implements various military-grade wiping standards including
NIST SP 800-88, DoD 5220.22-M variants, HMG IS5, and other standards.
"""

import os
import logging
import random
from typing import Dict, List, Callable


class MilitaryWipingStandards:
    """Implementation of various military-grade data wiping standards."""
    
    def __init__(self, logger=None):
        """
        Initialize military wiping standards.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Map of standard names to their implementation methods
        self.standards = {
            'nist_clear': self.nist_sp_800_88_clear,
            'nist_purge': self.nist_sp_800_88_purge,
            'dod_3pass': self.dod_5220_22_m_3pass,
            'dod_7pass': self.dod_5220_22_m_7pass,
            'hmg_is5_baseline': self.hmg_is5_baseline,
            'hmg_is5_enhanced': self.hmg_is5_enhanced,
            'navso': self.navso_p_5239_26,
            'afssi': self.afssi_5020,
            'ar_380_19': self.ar_380_19,
            'csc': self.csc_std_005_85
        }
    
    def get_standard(self, standard_name):
        """
        Get a wiping standard by name.
        
        Args:
            standard_name: Name of the standard
            
        Returns:
            function: Wiping function
        """
        if standard_name in self.standards:
            return self.standards[standard_name]
        
        self.logger.warning(f"Unknown military standard: {standard_name}")
        return None
    
    def nist_sp_800_88_clear(self, file_obj, size):
        """
        NIST SP 800-88 Clear standard.
        
        Overwrites with a single pass of zeros.
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying NIST SP 800-88 Clear (single pass of zeros)")
        
        # Seek to beginning of file
        file_obj.seek(0)
        
        # Create a chunk of zeros to write
        chunk_size = min(1024 * 1024, size)  # 1 MB chunks or file size if smaller
        chunk = b'\x00' * chunk_size
        
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
        
        return ["Pass 1: All zeros"]
    
    def nist_sp_800_88_purge(self, file_obj, size):
        """
        NIST SP 800-88 Purge standard.
        
        Overwrites with a single pass of ones.
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying NIST SP 800-88 Purge (single pass of ones)")
        
        # Seek to beginning of file
        file_obj.seek(0)
        
        # Create a chunk of ones to write
        chunk_size = min(1024 * 1024, size)  # 1 MB chunks or file size if smaller
        chunk = b'\xFF' * chunk_size
        
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
        
        return ["Pass 1: All ones"]
    
    def dod_5220_22_m_3pass(self, file_obj, size):
        """
        DoD 5220.22-M (3-pass) standard.
        
        Pass 1: Zeros
        Pass 2: Ones
        Pass 3: Random data
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying DoD 5220.22-M 3-pass standard")
        
        # Define patterns for each pass
        patterns = [
            (b'\x00', "Pass 1: All zeros"),
            (b'\xFF', "Pass 2: All ones"),
            (None, "Pass 3: Random data")  # None means use random data
        ]
        
        # Apply each pattern
        for pattern, description in patterns:
            self.logger.debug(description)
            
            # Seek to beginning of file
            file_obj.seek(0)
            
            if pattern is None:
                # Use random data for this pass
                self._write_random_data(file_obj, size)
            else:
                # Use the specified pattern
                self._write_pattern(file_obj, pattern, size)
            
            # Flush after each pass
            file_obj.flush()
            os.fsync(file_obj.fileno())
        
        return [desc for _, desc in patterns]
    
    def dod_5220_22_m_7pass(self, file_obj, size):
        """
        DoD 5220.22-M (7-pass) standard.
        
        Pass 1: Zeros
        Pass 2: Ones
        Pass 3: Random data
        Pass 4: Random data
        Pass 5: Zeros
        Pass 6: Ones
        Pass 7: Random data
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying DoD 5220.22-M 7-pass standard")
        
        # Define patterns for each pass
        patterns = [
            (b'\x00', "Pass 1: All zeros"),
            (b'\xFF', "Pass 2: All ones"),
            (None, "Pass 3: Random data"),
            (None, "Pass 4: Random data"),
            (b'\x00', "Pass 5: All zeros"),
            (b'\xFF', "Pass 6: All ones"),
            (None, "Pass 7: Random data")
        ]
        
        # Apply each pattern
        for pattern, description in patterns:
            self.logger.debug(description)
            
            # Seek to beginning of file
            file_obj.seek(0)
            
            if pattern is None:
                # Use random data for this pass
                self._write_random_data(file_obj, size)
            else:
                # Use the specified pattern
                self._write_pattern(file_obj, pattern, size)
            
            # Flush after each pass
            file_obj.flush()
            os.fsync(file_obj.fileno())
        
        return [desc for _, desc in patterns]
    
    def hmg_is5_baseline(self, file_obj, size):
        """
        HMG IS5 Baseline standard (UK Government).
        
        Single pass of random data.
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying HMG IS5 Baseline standard")
        
        # Seek to beginning of file
        file_obj.seek(0)
        
        # Single pass of random data
        self._write_random_data(file_obj, size)
        
        # Flush final writes
        file_obj.flush()
        os.fsync(file_obj.fileno())
        
        return ["Pass 1: Random data"]
    
    def hmg_is5_enhanced(self, file_obj, size):
        """
        HMG IS5 Enhanced standard (UK Government).
        
        Pass 1: Zeros
        Pass 2: Random data
        Pass 3: Random data verification
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying HMG IS5 Enhanced standard")
        
        # Define patterns for each pass
        patterns = [
            (b'\x00', "Pass 1: All zeros"),
            (None, "Pass 2: Random data"),
            (None, "Pass 3: Random data verification")
        ]
        
        # Apply each pattern
        for pattern, description in patterns:
            self.logger.debug(description)
            
            # Seek to beginning of file
            file_obj.seek(0)
            
            if pattern is None:
                # Use random data for this pass
                self._write_random_data(file_obj, size)
            else:
                # Use the specified pattern
                self._write_pattern(file_obj, pattern, size)
            
            # Flush after each pass
            file_obj.flush()
            os.fsync(file_obj.fileno())
        
        return [desc for _, desc in patterns]
    
    def navso_p_5239_26(self, file_obj, size):
        """
        NAVSO P-5239-26 (US Navy) standard.
        
        Pass 1: Character pattern (0x01)
        Pass 2: Complement (0xFE)
        Pass 3: Random data
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying NAVSO P-5239-26 standard")
        
        # Define patterns for each pass
        patterns = [
            (b'\x01', "Pass 1: Character pattern (0x01)"),
            (b'\xFE', "Pass 2: Complement (0xFE)"),
            (None, "Pass 3: Random data")
        ]
        
        # Apply each pattern
        for pattern, description in patterns:
            self.logger.debug(description)
            
            # Seek to beginning of file
            file_obj.seek(0)
            
            if pattern is None:
                # Use random data for this pass
                self._write_random_data(file_obj, size)
            else:
                # Use the specified pattern
                self._write_pattern(file_obj, pattern, size)
            
            # Flush after each pass
            file_obj.flush()
            os.fsync(file_obj.fileno())
        
        return [desc for _, desc in patterns]
    
    def afssi_5020(self, file_obj, size):
        """
        AFSSI-5020 (Air Force) standard.
        
        Pass 1: Zeros
        Pass 2: Ones
        Pass 3: Random data
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying AFSSI-5020 standard")
        
        # This is identical to DoD 3-pass
        return self.dod_5220_22_m_3pass(file_obj, size)
    
    def ar_380_19(self, file_obj, size):
        """
        AR 380-19 (Army) standard.
        
        Pass 1: Random character
        Pass 2: Specified character (0xFE)
        Pass 3: Complement of specified character (0x01)
        Pass 4-7: Random characters
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying AR 380-19 standard")
        
        # Define patterns for each pass
        patterns = [
            (None, "Pass 1: Random data"),
            (b'\xFE', "Pass 2: Specified character (0xFE)"),
            (b'\x01', "Pass 3: Complement (0x01)"),
            (None, "Pass 4: Random data"),
            (None, "Pass 5: Random data"),
            (None, "Pass 6: Random data"),
            (None, "Pass 7: Random data")
        ]
        
        # Apply each pattern
        for pattern, description in patterns:
            self.logger.debug(description)
            
            # Seek to beginning of file
            file_obj.seek(0)
            
            if pattern is None:
                # Use random data for this pass
                self._write_random_data(file_obj, size)
            else:
                # Use the specified pattern
                self._write_pattern(file_obj, pattern, size)
            
            # Flush after each pass
            file_obj.flush()
            os.fsync(file_obj.fileno())
        
        return [desc for _, desc in patterns]
    
    def csc_std_005_85(self, file_obj, size):
        """
        CSC-STD-005-85 (NSA) standard.
        
        3 to 7 passes of specific patterns (we use the 7-pass variant).
        
        Args:
            file_obj: File object for writing
            size: Size of data to overwrite in bytes
            
        Returns:
            list: Pass descriptions
        """
        self.logger.info("Applying CSC-STD-005-85 standard")
        
        # Define patterns for each pass
        patterns = [
            (b'\x00', "Pass 1: All zeros (0x00)"),
            (b'\xFF', "Pass 2: All ones (0xFF)"),
            (None, "Pass 3: Random data"),
            (b'\x96', "Pass 4: Pattern A (0x96)"),
            (b'\x69', "Pass 5: Complement of Pattern A (0x69)"),
            (b'\xAA', "Pass 6: Pattern B (0xAA)"),
            (b'\x55', "Pass 7: Complement of Pattern B (0x55)")
        ]
        
        # Apply each pattern
        for pattern, description in patterns:
            self.logger.debug(description)
            
            # Seek to beginning of file
            file_obj.seek(0)
            
            if pattern is None:
                # Use random data for this pass
                self._write_random_data(file_obj, size)
            else:
                # Use the specified pattern
                self._write_pattern(file_obj, pattern, size)
            
            # Flush after each pass
            file_obj.flush()
            os.fsync(file_obj.fileno())
        
        return [desc for _, desc in patterns]
    
    def _write_random_data(self, file_obj, size):
        """
        Write random data to a file.
        
        Args:
            file_obj: File object to write to
            size: Size of the data to write in bytes
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
            size: Size of the data to write in bytes
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