"""
Wiping patterns for SecureEraser.

This module defines the available wiping patterns for different methods.
"""

import random
import logging
from typing import Dict, List, Optional, Union, Any, Callable


class WipePatterns:
    """
    Static class for wiping patterns.
    """
    
    # Registered wiping methods
    _methods = {}
    
    # Method names mapping
    _method_names = {
        "standard": "Standard Random Data",
        "dod": "DoD 5220.22-M",
        "gutmann": "Gutmann 35-pass Method",
        "paranoid": "Paranoid Enhanced Method"
    }
    
    # Method descriptions mapping
    _method_descriptions = {
        "standard": "Basic multi-pass overwrite with random data",
        "dod": "Department of Defense 5220.22-M standard",
        "gutmann": "Peter Gutmann's 35-pass secure deletion method",
        "paranoid": "Enhanced combined method with increased security"
    }
    
    @classmethod
    def calculate_passes_for_method(cls, method: str, requested_passes: int) -> int:
        """
        Calculate the actual number of passes based on method and requested passes.
        
        Args:
            method: Wiping method
            requested_passes: Requested number of passes
            
        Returns:
            Actual number of passes to use
        """
        method = method.lower()
        
        if method == "standard":
            # Standard method uses the requested passes
            return max(1, requested_passes)
            
        elif method == "dod":
            # DoD method requires minimum 3 passes, but can do more
            return max(3, requested_passes)
            
        elif method == "gutmann":
            # Gutmann method is fixed at 35 passes
            return 35
            
        elif method == "paranoid":
            # Paranoid method combines DoD and Gutmann, minimum 42 passes
            return max(42, requested_passes)
            
        else:
            # For registered custom methods, use their pattern count
            if method in cls._methods:
                return len(cls._methods[method])
            
            # Unknown method, fall back to standard with requested passes
            return max(1, requested_passes)
    
    @classmethod
    def get_pattern_for_pass(cls, method: str, pass_number: int) -> Optional[bytes]:
        """
        Get the pattern for a specific pass of a wiping method.
        
        Args:
            method: Wiping method
            pass_number: Pass number (0-based)
            
        Returns:
            Pattern bytes or None for random data
        """
        method = method.lower()
        
        if method == "standard":
            # Standard method uses random data for all passes
            return None
            
        elif method == "dod":
            # DoD 5220.22-M method
            # Pass 1: All zeros (0x00)
            # Pass 2: All ones (0xFF)
            # Pass 3+: Random data
            if pass_number == 0:
                return bytes([0x00] * 512)  # 512-byte block of zeros
            elif pass_number == 1:
                return bytes([0xFF] * 512)  # 512-byte block of ones
            else:
                return None  # Random data
                
        elif method == "gutmann":
            # Gutmann 35-pass method
            if pass_number < 4:
                # Passes 1-4: Random data
                return None
            elif pass_number < 10:
                # Passes 5-10: Static patterns
                patterns = [
                    bytes([0x55] * 512),  # 5: 01010101
                    bytes([0xAA] * 512),  # 6: 10101010
                    bytes([0x92, 0x49, 0x24] * (512 // 3)),  # 7: 10010010, 01001001, 00100100
                    bytes([0x49, 0x24, 0x92] * (512 // 3)),  # 8: 01001001, 00100100, 10010010
                    bytes([0x24, 0x92, 0x49] * (512 // 3)),  # 9: 00100100, 10010010, 01001001
                ]
                return patterns[pass_number - 4]
            elif pass_number < 26:
                # Passes 11-25: Static patterns (more complex)
                # Each pass writes a specific byte pattern
                byte_patterns = [
                    0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                    0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF
                ]
                pattern_idx = (pass_number - 10) % len(byte_patterns)
                return bytes([byte_patterns[pattern_idx]] * 512)
            elif pass_number < 31:
                # Passes 26-30: More complex patterns
                patterns = [
                    bytes([0x92, 0x49, 0x24] * (512 // 3)),  # 26: 10010010, 01001001, 00100100
                    bytes([0x49, 0x24, 0x92] * (512 // 3)),  # 27: 01001001, 00100100, 10010010
                    bytes([0x24, 0x92, 0x49] * (512 // 3)),  # 28: 00100100, 10010010, 01001001
                    bytes([0x6D, 0xB6, 0xDB] * (512 // 3)),  # 29: 01101101, 10110110, 11011011
                    bytes([0xB6, 0xDB, 0x6D] * (512 // 3)),  # 30: 10110110, 11011011, 01101101
                ]
                return patterns[pass_number - 26]
            else:
                # Passes 31-35: Random data
                return None
                
        elif method == "paranoid":
            # Paranoid method combines DoD and Gutmann with extras
            if pass_number < 7:
                # First 7 passes: DoD 7-pass variant
                patterns = [
                    bytes([0xF6] * 512),  # Pass 1: 0xF6
                    bytes([0x00] * 512),  # Pass 2: All zeros
                    bytes([0xFF] * 512),  # Pass 3: All ones
                    None,                 # Pass 4: Random data
                    bytes([0x00] * 512),  # Pass 5: All zeros
                    bytes([0xFF] * 512),  # Pass 6: All ones
                    None                  # Pass 7: Random data
                ]
                return patterns[pass_number]
            elif pass_number < 42:
                # Next 35 passes: Gutmann method
                return cls.get_pattern_for_pass("gutmann", pass_number - 7)
            else:
                # Additional passes: Random data
                return None
                
        else:
            # Check for registered custom methods
            if method in cls._methods:
                patterns = cls._methods[method]
                if pass_number < len(patterns):
                    return patterns[pass_number]
                else:
                    return None  # Default to random if out of range
            
            # Unknown method, use random data
            return None
    
    @classmethod
    def get_pattern_name(cls, method: str, pass_number: int) -> str:
        """
        Get a human-readable name for the pattern used in a pass.
        
        Args:
            method: Wiping method
            pass_number: Pass number (0-based)
            
        Returns:
            Pattern name
        """
        pattern = cls.get_pattern_for_pass(method, pass_number)
        
        if pattern is None:
            return "Random Data"
            
        # Check if it's all zeros
        if all(b == 0x00 for b in pattern[:16]):
            return "All Zeros (0x00)"
            
        # Check if it's all ones
        if all(b == 0xFF for b in pattern[:16]):
            return "All Ones (0xFF)"
            
        # Check if it's alternating
        if pattern[:16] == bytes([0x55] * 16):
            return "Alternating 01010101"
            
        if pattern[:16] == bytes([0xAA] * 16):
            return "Alternating 10101010"
            
        # Check if it's a repeating single byte
        if all(b == pattern[0] for b in pattern[:16]):
            return f"Fixed Byte 0x{pattern[0]:02X}"
            
        # For other patterns, show a prefix
        prefix = pattern[:8].hex()
        return f"Pattern {prefix}..."
    
    @classmethod
    def get_method_description(cls, method: str) -> str:
        """
        Get a description of a wiping method.
        
        Args:
            method: Wiping method
            
        Returns:
            Method description
        """
        method = method.lower()
        
        if method in cls._method_descriptions:
            return cls._method_descriptions[method]
            
        # Check for registered custom methods
        if method in cls._methods:
            # Return the registered description or a generic one
            return f"Custom method: {method}"
            
        return "Unknown wiping method"
    
    @classmethod
    def get_method_name(cls, method: str) -> str:
        """
        Get a human-readable name for a wiping method.
        
        Args:
            method: Wiping method
            
        Returns:
            Method name
        """
        method = method.lower()
        
        if method in cls._method_names:
            return cls._method_names[method]
            
        # Check for registered custom methods
        if method in cls._methods:
            # Capitalize method name if no custom name is registered
            return method.title()
            
        return "Unknown Method"
    
    @classmethod
    def generate_pattern_data(cls, pattern: Optional[bytes], size: int) -> bytes:
        """
        Generate data based on a pattern.
        
        Args:
            pattern: Pattern bytes or None for random data
            size: Size of data to generate
            
        Returns:
            Generated data
        """
        if pattern is None:
            # Generate random data
            return bytes(random.getrandbits(8) for _ in range(size))
            
        # Repeat the pattern to fill the requested size
        pattern_size = len(pattern)
        repeats = (size + pattern_size - 1) // pattern_size
        return (pattern * repeats)[:size]
    
    @classmethod
    def register_method(cls, method_name: str, patterns: List[bytes],
                       display_name: Optional[str] = None,
                       description: Optional[str] = None) -> None:
        """
        Register a custom wiping method.
        
        Args:
            method_name: Method identifier
            patterns: List of patterns for each pass
            display_name: Human-readable name (optional)
            description: Method description (optional)
        """
        method_name = method_name.lower()
        
        # Register the patterns
        cls._methods[method_name] = patterns
        
        # Register name and description if provided
        if display_name:
            cls._method_names[method_name] = display_name
            
        if description:
            cls._method_descriptions[method_name] = description