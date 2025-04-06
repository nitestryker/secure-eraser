"""
Cryptographic verification functionality for the Secure Eraser tool.
"""

import hashlib
import hmac
import uuid
import os
import datetime
import json
import logging
from typing import Dict, List, Optional, Union


# Default hash algorithms to use for verification
DEFAULT_HASH_ALGORITHMS = ['sha256', 'sha3_256']


class Verification:
    """
    Handles cryptographic verification of secure wiping operations.
    """
    
    def __init__(self, hash_algorithms: Optional[List[str]] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize verification with specified hash algorithms.
        
        Args:
            hash_algorithms: List of hash algorithms to use (must be supported by hashlib)
            logger: Logger instance to use (if None, a new one will be created)
        """
        self.hash_algorithms = hash_algorithms or DEFAULT_HASH_ALGORITHMS
        self.logger = logger or logging.getLogger(__name__)
        
        # Validate hash algorithms
        for algo in self.hash_algorithms:
            if not hasattr(hashlib, algo):
                self.logger.warning(f"Hash algorithm '{algo}' not available in hashlib, removing from list")
                self.hash_algorithms.remove(algo)
        
        if not self.hash_algorithms:
            self.logger.warning("No valid hash algorithms specified, using default")
            self.hash_algorithms = DEFAULT_HASH_ALGORITHMS
            
        # Initialize verification data
        self.verification_data = {
            "wiped_items": [],
            "timestamp": datetime.datetime.now().isoformat(),
            "hash_algorithms": self.hash_algorithms
        }
    
    def compute_file_hash(self, file_path: str, algorithms: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Compute hash of a file using multiple algorithms.
        
        Args:
            file_path: Path to the file
            algorithms: List of hash algorithms to use
            
        Returns:
            Dictionary mapping algorithm names to hash values
        """
        if not os.path.isfile(file_path):
            self.logger.error(f"File not found: {file_path}")
            return {}
        
        # Use instance algorithms if none specified
        algorithms = algorithms or self.hash_algorithms
        hash_objects = {algo: getattr(hashlib, algo)() for algo in algorithms if hasattr(hashlib, algo)}
        
        if not hash_objects:
            self.logger.error("No valid hash algorithms available")
            return {}
            
        try:
            # Process file in chunks to handle large files
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    for hash_obj in hash_objects.values():
                        hash_obj.update(chunk)
                        
            # Get hexadecimal digest of each hash
            return {algo: hash_obj.hexdigest() for algo, hash_obj in hash_objects.items()}
        
        except Exception as e:
            self.logger.error(f"Error computing hash for {file_path}: {e}")
            return {}
    
    def create_verification_record(self, file_path: str, status: str, 
                                   before_hashes: Optional[Dict[str, str]] = None, 
                                   after_hashes: Optional[Dict[str, str]] = None,
                                   size: int = 0) -> Dict:
        """
        Create a verification record for a file.
        
        Args:
            file_path: Path to the file
            status: Status of the wiping operation
            before_hashes: Dictionary of hash values before wiping
            after_hashes: Dictionary of hash values after wiping
            size: Size of the file in bytes
            
        Returns:
            Dictionary with verification information
        """
        before_hashes = before_hashes or {}
        after_hashes = after_hashes or {}
        
        # Check if hashes changed for each algorithm
        algorithms_verified = {}
        
        for algo in before_hashes.keys():
            # A hash is considered verified if it changed after wiping
            # (which indicates the data was actually modified)
            if algo in after_hashes:
                algorithms_verified[algo] = before_hashes[algo] != after_hashes[algo]
        
        # Determine overall verification status
        verified = all(algorithms_verified.values()) if algorithms_verified else False
        
        # Create record
        record = {
            "path": file_path,
            "file_name": os.path.basename(file_path),
            "status": status,
            "timestamp": datetime.datetime.now().isoformat(),
            "size": size,
            "verification": {
                "verified": verified,
                "before_hashes": before_hashes,
                "after_hashes": after_hashes,
                "algorithms_verified": algorithms_verified
            }
        }
        
        # Add to verification data
        self.verification_data["wiped_items"].append(record)
        
        return record
        
    def sign_data(self, data: Dict, signature_key: Optional[str] = None) -> Dict:
        """
        Digitally sign data using HMAC.
        
        Args:
            data: Data to sign as a dictionary
            signature_key: Key to use for signing (if None, a random key will be generated)
            
        Returns:
            Dictionary with signature information
        """
        # Generate a key if not provided
        key = signature_key or str(uuid.uuid4())
        
        # Convert data to JSON string for consistent hashing
        data_str = json.dumps(data, sort_keys=True)
        
        # Sign with HMAC-SHA256
        signature = hmac.new(
            key.encode('utf-8'),
            data_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Return signature information
        return {
            "algorithm": "HMAC-SHA256",
            "timestamp": datetime.datetime.now().isoformat(),
            "value": signature,
            "key_id": key[:8] + "..." if len(key) > 8 else key  # Only show part of the key
        }