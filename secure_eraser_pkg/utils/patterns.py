"""
Wiping patterns and pattern generation utilities.
"""

import random
from typing import Union, List, Tuple, Optional


# Standard patterns for secure data wiping
class WipePatterns:
    """
    Collection of standard wiping patterns for different security levels.
    """
    # DoD 5220.22-M standard wipe patterns
    DOD_PATTERNS = [
        b'\x00',                        # Pass 1: All zeros
        b'\xFF',                        # Pass 2: All ones
        b'\x00\xFF\x00\xFF\x00\xFF',    # Pass 3: Alternating bit pattern
        b'\x55\xAA\x55\xAA\x55\xAA',    # Pass 4: Another alternating bit pattern
        b'\x92\x49\x24',                # Pass 5: Random pattern
        b'\x49\x92\x24\x49\x92',        # Pass 6: Another random pattern
        b'\xDB\xB6\xDB\x6D\xB6\xDB',    # Pass 7: Another random pattern
    ]
    
    # Gutmann 35-pass method patterns (simplified representation)
    GUTMANN_PASSES = 35
    
    # Dictionary mapping method names to minimum pass counts
    METHOD_PASSES = {
        "standard": 3,     # Basic method, user-defined passes
        "dod": 7,          # DoD 5220.22-M standard
        "gutmann": 35,     # Gutmann method
        "paranoid": 49,    # Combined DoD + Gutmann + additional
    }
    
    @staticmethod
    def get_pattern_for_pass(method: str, pass_index: int) -> bytes:
        """
        Get the appropriate pattern for a specific pass based on the wiping method.
        
        Args:
            method: Wiping method (standard, dod, gutmann, paranoid)
            pass_index: Current pass number (0-based index)
            
        Returns:
            Byte pattern to use for the current pass
        """
        method = method.lower()
        
        # Standard method uses simple patterns
        if method == "standard":
            if pass_index == 0:
                return b'\x00'  # First pass: zeros
            elif pass_index == 1:
                return b'\xFF'  # Second pass: ones
            else:
                return b''  # Random data for other passes
                
        # DoD method uses specific patterns
        elif method == "dod":
            if pass_index < len(WipePatterns.DOD_PATTERNS):
                return WipePatterns.DOD_PATTERNS[pass_index]
            return b''  # Random data for passes beyond predefined patterns
            
        # Gutmann method uses a mix of specific patterns and random data
        elif method == "gutmann" or method == "paranoid":
            # Simplification: use specific patterns for first few passes, 
            # then random for remaining
            if pass_index < len(WipePatterns.DOD_PATTERNS):
                return WipePatterns.DOD_PATTERNS[pass_index]
            return b''  # Random data for other passes
            
        # Default to random data
        return b''

    @staticmethod
    def get_pattern_name(method: str, pass_index: int) -> str:
        """
        Get a human-readable name for the pattern used in a specific pass.
        
        Args:
            method: Wiping method (standard, dod, gutmann, paranoid)
            pass_index: Current pass number (0-based index)
            
        Returns:
            Human-readable description of the pattern
        """
        method = method.lower()
        
        # Get the pattern for this pass
        pattern = WipePatterns.get_pattern_for_pass(method, pass_index)
        
        # Return appropriate pattern name
        if pattern == b'\x00':
            return "zeros"
        elif pattern == b'\xFF':
            return "ones"
        elif pattern == b'\x00\xFF\x00\xFF\x00\xFF':
            return "alternating 0/1 bits"
        elif pattern == b'\x55\xAA\x55\xAA\x55\xAA':
            return "alternating 01/10 bits"
        else:
            # For other patterns or random data
            if method == "dod" and pass_index < len(WipePatterns.DOD_PATTERNS):
                return f"DoD pattern {pass_index+1}"
            elif method == "gutmann":
                if pass_index < 4:
                    return f"Gutmann random pattern {pass_index+1}"
                elif pass_index < 10:
                    return f"Gutmann static pattern {pass_index+1}"
                else:
                    return f"Gutmann random pattern {pass_index+1}"
            else:
                return f"random data (pass {pass_index+1})"

    @staticmethod
    def generate_pattern_data(pattern: bytes, chunk_size: int) -> bytes:
        """
        Generate a chunk of data with the specified pattern.
        
        Args:
            pattern: Byte pattern to use
            chunk_size: Size of the chunk to generate in bytes
            
        Returns:
            Byte string of the specified size filled with the pattern
        """
        # If pattern is empty, generate random data
        if not pattern:
            return bytes(random.getrandbits(8) for _ in range(chunk_size))
            
        # If pattern is shorter than chunk size, repeat it
        if len(pattern) < chunk_size:
            full_repeats = chunk_size // len(pattern)
            remainder = chunk_size % len(pattern)
            return pattern * full_repeats + pattern[:remainder]
            
        # If pattern is longer than chunk size, truncate it
        return pattern[:chunk_size]

    @staticmethod
    def calculate_passes_for_method(method: str, user_passes: int) -> int:
        """
        Calculate the actual number of passes to use based on the method and user-specified count.
        
        Args:
            method: Wiping method (standard, dod, gutmann, paranoid)
            user_passes: User-specified number of passes
            
        Returns:
            Actual number of passes to perform
        """
        method = method.lower()
        min_passes = WipePatterns.METHOD_PASSES.get(method, 3)
        
        if method == "standard":
            return max(1, user_passes)  # At least 1 pass for standard method
        else:
            return max(min_passes, user_passes)  # At least the minimum required for the method