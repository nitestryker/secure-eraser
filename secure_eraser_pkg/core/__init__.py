"""
Core functionality for the Secure Eraser tool.
"""

import logging
import math
from typing import Dict, List, Optional, Union

from secure_eraser_pkg.core.eraser import SecureEraser
from secure_eraser_pkg.core.verification import Verification
from secure_eraser_pkg.utils.system_info import get_system_info


class SecureEraserWithVerification(SecureEraser, Verification):
    """
    Combined class that provides secure deletion with optional cryptographic verification.
    """
    
    def __init__(self, passes: int = 3, method: str = "standard", 
                 verify: bool = False, hash_algorithms: Optional[List[str]] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize with the number of overwrite passes, wiping method, and verification options.
        
        Args:
            passes: Number of overwrite passes (higher = more secure but slower)
            method: Wiping method - "standard", "dod", "gutmann", or "paranoid"
            verify: Whether to verify the wiping process with cryptographic hashes
            hash_algorithms: List of hash algorithms to use for verification
            logger: Logger instance to use (if None, a new one will be created)
        """
        # Initialize base classes
        SecureEraser.__init__(self, passes, method, verify, logger)
        
        if verify:
            Verification.__init__(self, hash_algorithms, logger)
            
        # Store system information
        self.system_info = get_system_info()