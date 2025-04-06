"""
Verification module for the SecureEraser tool.

This module extends the base SecureEraser with cryptographic verification capabilities.
"""

import os
import logging
import hashlib
import time
import json
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

from secure_eraser_pkg.core.eraser import SecureEraser
from secure_eraser_pkg.core.security.military_standards import MilitaryWipingStandards


class SecureEraserWithVerification(SecureEraser):
    """
    Extends the SecureEraser with cryptographic verification capabilities.
    """
    
    def __init__(self, passes=3, method="standard", verify=False, hash_algorithms=None, 
                 logger=None, **kwargs):
        """
        Initialize the secure eraser with verification capabilities.
        
        Args:
            passes: Number of overwrite passes
            method: Wiping method (standard, dod, gutmann, paranoid, or military standards)
            verify: Enable verification
            hash_algorithms: Hash algorithms to use for verification
            logger: Logger instance
            **kwargs: Additional arguments
        """
        super().__init__(passes=passes, method=method, logger=logger, **kwargs)
        
        self.verify = verify
        self.hash_algorithms = hash_algorithms or ['sha256', 'sha512']
        self.verification_data = {
            'timestamp': time.ctime(),
            'wiping_method': method,
            'passes': passes,
            'verification_enabled': verify,
            'algorithms_used': self.hash_algorithms,
            'items': []
        }
        
        # Initialize military wiping standards if we're using one
        self.military_standards = None
        if method in ['nist_clear', 'nist_purge', 'dod_3pass', 'dod_7pass', 
                      'hmg_is5_baseline', 'hmg_is5_enhanced', 'navso', 
                      'afssi', 'ar_380_19', 'csc']:
            self.military_standards = MilitaryWipingStandards(logger=logger)
        
    def secure_delete_file(self, file_path) -> bool:
        """
        Securely delete a file with verification.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            bool: Success or failure
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File {file_path} does not exist")
            return False
            
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # Create verification record
        item_record = {
            'path': file_path,
            'file_name': file_name,
            'size': file_size,
            'status': 'pending',
            'verification': {
                'verified': False,
                'before_hashes': {},
                'after_hashes': {},
                'algorithms_verified': {}
            }
        }
        
        # Compute hashes before wiping if verification is enabled
        if self.verify:
            item_record['verification']['before_hashes'] = self.compute_file_hash(file_path)
        
        # Delete the file
        start_time = time.time()
        success = super().secure_delete_file(file_path)
        elapsed_time = time.time() - start_time
        
        # Update record
        item_record['status'] = 'completed' if success else 'failed'
        item_record['elapsed_time'] = elapsed_time
        
        # Compute hashes after wiping if verification is enabled and the file still exists
        # (which it shouldn't, but we need to check for verification)
        if self.verify and os.path.exists(file_path):
            item_record['verification']['after_hashes'] = self.compute_file_hash(file_path)
            
            # Check if hashes changed (they should)
            for algo in self.hash_algorithms:
                before = item_record['verification']['before_hashes'].get(algo)
                after = item_record['verification']['after_hashes'].get(algo)
                
                if before and after and before != after:
                    item_record['verification']['algorithms_verified'][algo] = True
                else:
                    item_record['verification']['algorithms_verified'][algo] = False
            
            # Consider verified if all algorithms report change
            item_record['verification']['verified'] = all(
                item_record['verification']['algorithms_verified'].values()
            )
        elif self.verify:
            # If the file doesn't exist anymore, consider it verified
            item_record['verification']['verified'] = True
            for algo in self.hash_algorithms:
                item_record['verification']['algorithms_verified'][algo] = True
        
        # Add to verification data
        self.verification_data['items'].append(item_record)
        
        return success
    
    def secure_delete_directory(self, directory_path) -> bool:
        """
        Securely delete a directory with verification.
        
        Args:
            directory_path: Path to the directory to delete
            
        Returns:
            bool: Success or failure
        """
        if not os.path.exists(directory_path):
            self.logger.error(f"Directory {directory_path} does not exist")
            return False
            
        # Get total size of the directory
        total_size = 0
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):  # Check if file exists (could have been deleted by another process)
                    total_size += os.path.getsize(file_path)
        
        directory_name = os.path.basename(directory_path)
        
        # Create verification record
        item_record = {
            'path': directory_path,
            'file_name': directory_name,
            'size': total_size,
            'status': 'pending',
            'verification': {
                'verified': False,
                'files_processed': 0,
                'files_verified': 0
            }
        }
        
        # Delete the directory
        start_time = time.time()
        success = super().secure_delete_directory(directory_path)
        elapsed_time = time.time() - start_time
        
        # Update record
        item_record['status'] = 'completed' if success else 'failed'
        item_record['elapsed_time'] = elapsed_time
        
        # Verification is implied for directories (we verify individual files)
        if self.verify:
            item_record['verification']['verified'] = not os.path.exists(directory_path)
        
        # Add to verification data
        self.verification_data['items'].append(item_record)
        
        return success
    
    def compute_file_hash(self, file_path) -> Dict[str, str]:
        """
        Compute hash of a file using multiple algorithms.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict: Hash values by algorithm
        """
        result = {}
        
        try:
            for algorithm in self.hash_algorithms:
                if algorithm == 'md5':
                    hash_obj = hashlib.md5()
                elif algorithm == 'sha1':
                    hash_obj = hashlib.sha1()
                elif algorithm == 'sha256':
                    hash_obj = hashlib.sha256()
                elif algorithm == 'sha512':
                    hash_obj = hashlib.sha512()
                elif algorithm == 'sha3_256':
                    hash_obj = hashlib.sha3_256()
                elif algorithm == 'sha3_512':
                    hash_obj = hashlib.sha3_512()
                else:
                    self.logger.warning(f"Unsupported hash algorithm: {algorithm}, skipping")
                    continue
                
                with open(file_path, 'rb') as f:
                    # Read and update in chunks to handle large files
                    chunk_size = 8192  # 8KB chunks
                    chunk = f.read(chunk_size)
                    while chunk:
                        hash_obj.update(chunk)
                        chunk = f.read(chunk_size)
                
                result[algorithm] = hash_obj.hexdigest()
                
        except Exception as e:
            self.logger.error(f"Error computing hash for {file_path}: {e}")
            
        return result
    
    def create_verification_record(self, path, status, size=0) -> Dict:
        """
        Create a verification record for a file or directory.
        
        Args:
            path: Path to the file or directory
            status: Status of the operation
            size: Size of the file or directory
            
        Returns:
            Dict: Verification record
        """
        return {
            'path': path,
            'file_name': os.path.basename(path),
            'size': size,
            'status': status,
            'timestamp': time.ctime(),
            'verification': {
                'verified': False,
                'before_hashes': {},
                'after_hashes': {},
                'algorithms_verified': {}
            }
        }