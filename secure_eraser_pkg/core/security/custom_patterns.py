"""
Custom wiping patterns for the SecureEraser tool.

This module handles the management of custom wiping patterns created by users.
"""

import os
import logging
import json
import random
import binascii
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple


class CustomPatternManager:
    """Manages custom wiping patterns for secure deletion."""
    
    def __init__(self, config_dir=None, logger=None):
        """
        Initialize the custom pattern manager.
        
        Args:
            config_dir: Directory to store pattern configurations
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Set default config directory
        if config_dir is None:
            self.config_dir = os.path.join(
                os.path.expanduser("~"),
                ".config",
                "secure_eraser"
            )
        else:
            self.config_dir = config_dir
            
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Path to patterns file
        self.patterns_file = os.path.join(self.config_dir, "custom_patterns.json")
        
        # Load existing patterns
        self.patterns = self._load_patterns()
        
    def get_all_patterns(self) -> Dict:
        """
        Get all available custom patterns.
        
        Returns:
            Dict: Dictionary of all patterns and their configurations
        """
        return self.patterns
        
    def get_available_generators(self) -> Dict[str, str]:
        """
        Get available pattern generators.
        
        Returns:
            Dict: Dictionary of generator names and descriptions
        """
        return {
            "random": "Cryptographically secure random data",
            "zeros": "All zeros (0x00)",
            "ones": "All ones (0xFF)",
            "alternating": "Alternating bits (0xAA, 0x55)",
            "random_complement": "Random data followed by its complement",
            "ascii_noise": "Random printable ASCII characters",
            "fibonacci": "Fibonacci sequence bytes",
            "counter": "Incrementing counter bytes",
            "random_blocks": "Random-size blocks of random data",
        }
        
        # Load existing patterns
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict:
        """
        Load custom patterns from config file.
        
        Returns:
            Dict: Dictionary of custom patterns
        """
        if not os.path.exists(self.patterns_file):
            # Create empty patterns file if it doesn't exist
            self._save_patterns({})
            return {}
            
        try:
            with open(self.patterns_file, 'r') as f:
                patterns = json.load(f)
                
            # Validate the loaded patterns
            for name, pattern in patterns.items():
                if not self._validate_pattern(pattern):
                    self.logger.warning(f"Invalid pattern found: {name}")
                    patterns.pop(name)
                    
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error loading patterns: {e}")
            return {}
    
    def _save_patterns(self, patterns: Dict) -> bool:
        """
        Save custom patterns to config file.
        
        Args:
            patterns: Dictionary of custom patterns
            
        Returns:
            bool: Success or failure
        """
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving patterns: {e}")
            return False
    
    def _validate_pattern(self, pattern: Dict) -> bool:
        """
        Validate a custom pattern.
        
        Args:
            pattern: Pattern to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check if pattern has required fields
        if not all(key in pattern for key in ['type', 'description']):
            return False
            
        # Validate based on pattern type
        pattern_type = pattern.get('type')
        
        if pattern_type == 'hex':
            # Hex patterns need a valid hex value
            hex_value = pattern.get('hex_value', '')
            return self._is_valid_hex(hex_value)
            
        elif pattern_type == 'multi_pass':
            # Multi-pass patterns need a list of passes
            passes = pattern.get('passes', [])
            return isinstance(passes, list) and all(
                isinstance(p, dict) and 'type' in p for p in passes
            )
            
        elif pattern_type == 'generator':
            # Generator patterns need a valid generator name
            generator = pattern.get('generator')
            return generator in [
                'random', 'zeros', 'ones', 'alternating',
                'random_complement', 'ascii_noise', 'fibonacci',
                'counter', 'random_blocks'
            ]
            
        # Unknown pattern type
        return False
    
    def _is_valid_hex(self, hex_string: str) -> bool:
        """
        Check if a string is a valid hex string.
        
        Args:
            hex_string: Hex string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Remove any spaces or other formatting characters
        hex_string = re.sub(r'[^0-9A-Fa-f]', '', hex_string)
        
        # Check if the string contains only hex characters and has even length
        return bool(re.match(r'^[0-9A-Fa-f]*$', hex_string)) and len(hex_string) % 2 == 0
    
    def create_pattern(self, name: str, pattern_config: Dict) -> bool:
        """
        Create a new custom pattern.
        
        Args:
            name: Name of the pattern
            pattern_config: Configuration for the pattern
            
        Returns:
            bool: Success or failure
        """
        # Check if pattern name already exists
        if name in self.patterns:
            self.logger.warning(f"Pattern '{name}' already exists")
            return False
            
        # Validate the pattern
        if not self._validate_pattern(pattern_config):
            self.logger.error(f"Invalid pattern configuration: {pattern_config}")
            return False
            
        # Add the pattern
        self.patterns[name] = pattern_config
        
        # Save the updated patterns
        return self._save_patterns(self.patterns)
    
    def create_hex_pattern(self, name: str, hex_value: str, description: str = "") -> bool:
        """
        Create a new hex pattern.
        
        Args:
            name: Name of the pattern
            hex_value: Hex string for the pattern
            description: Optional description
            
        Returns:
            bool: Success or failure
        """
        # Validate hex string
        if not self._is_valid_hex(hex_value):
            self.logger.error(f"Invalid hex value: {hex_value}")
            return False
            
        # Remove any spaces or other formatting characters
        clean_hex = re.sub(r'[^0-9A-Fa-f]', '', hex_value)
        
        # Create pattern config
        pattern_config = {
            'type': 'hex',
            'hex_value': clean_hex,
            'description': description if description else f"Custom hex pattern: {clean_hex[:16]}..."
        }
        
        return self.create_pattern(name, pattern_config)
    
    def delete_pattern(self, name: str) -> bool:
        """
        Delete a custom pattern.
        
        Args:
            name: Name of the pattern to delete
            
        Returns:
            bool: Success or failure
        """
        # Check if pattern exists
        if name not in self.patterns:
            self.logger.warning(f"Pattern '{name}' does not exist")
            return False
            
        # Remove the pattern
        self.patterns.pop(name)
        
        # Save the updated patterns
        return self._save_patterns(self.patterns)
    
    def get_pattern(self, name: str) -> Optional[Dict]:
        """
        Get a custom pattern by name.
        
        Args:
            name: Name of the pattern
            
        Returns:
            Optional[Dict]: Pattern config or None if not found
        """
        return self.patterns.get(name)
    
    def format_patterns_list(self) -> Dict:
        """
        Format custom patterns for display.
        
        Returns:
            Dict: Dictionary of pattern names and formatted descriptions
        """
        return {
            name: {
                'type': pattern.get('type'),
                'description': pattern.get('description')
            }
            for name, pattern in self.patterns.items()
        }
    
    def apply_pattern(self, file_obj, size: int, pattern_name: str) -> bool:
        """
        Apply a custom pattern to a file.
        
        Args:
            file_obj: File object to write to
            size: Size of the file in bytes
            pattern_name: Name of the pattern to apply
            
        Returns:
            bool: Success or failure
        """
        # Get the pattern
        pattern = self.get_pattern(pattern_name)
        
        if pattern is None:
            self.logger.error(f"Pattern '{pattern_name}' not found")
            return False
            
        try:
            # Apply the pattern based on its type
            pattern_type = pattern.get('type')
            
            if pattern_type == 'hex':
                # Apply hex pattern
                hex_value = pattern.get('hex_value', '')
                if not hex_value:
                    raise ValueError("Hex pattern has no value")
                    
                # Convert hex to bytes
                byte_pattern = binascii.unhexlify(hex_value)
                self._write_pattern(file_obj, byte_pattern, size)
                
            elif pattern_type == 'multi_pass':
                # Apply multi-pass pattern
                passes = pattern.get('passes', [])
                if not passes:
                    raise ValueError("Multi-pass pattern has no passes")
                    
                for pass_num, pass_config in enumerate(passes, 1):
                    self.logger.debug(f"Applying multi-pass pattern: pass {pass_num}/{len(passes)}")
                    
                    # Seek to beginning of file for each pass
                    file_obj.seek(0)
                    
                    # Apply the pass
                    self._apply_pass(file_obj, size, pass_config)
                    
                    # Flush after each pass
                    file_obj.flush()
                    os.fsync(file_obj.fileno())
                    
            elif pattern_type == 'generator':
                # Apply generator pattern
                generator = pattern.get('generator')
                if not generator:
                    raise ValueError("Generator pattern has no generator")
                    
                self._apply_generator(file_obj, size, generator, pattern.get('params', {}))
                
            else:
                self.logger.error(f"Unknown pattern type: {pattern_type}")
                return False
                
            # Flush final writes
            file_obj.flush()
            os.fsync(file_obj.fileno())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying pattern: {e}")
            return False
    
    def _apply_pass(self, file_obj, size: int, pass_config: Dict) -> None:
        """
        Apply a single pass of a multi-pass pattern.
        
        Args:
            file_obj: File object to write to
            size: Size of the file in bytes
            pass_config: Configuration for this pass
        """
        pass_type = pass_config.get('type')
        
        if pass_type == 'hex':
            # Apply hex pattern
            hex_value = pass_config.get('hex_value', '')
            if not hex_value:
                raise ValueError("Hex pass has no value")
                
            # Convert hex to bytes
            byte_pattern = binascii.unhexlify(hex_value)
            self._write_pattern(file_obj, byte_pattern, size)
            
        elif pass_type == 'random':
            # Apply random data
            self._write_random_data(file_obj, size)
            
        elif pass_type == 'zeros':
            # Apply zeros
            self._write_pattern(file_obj, b'\x00', size)
            
        elif pass_type == 'ones':
            # Apply ones
            self._write_pattern(file_obj, b'\xFF', size)
            
        elif pass_type == 'generator':
            # Apply generator pattern
            generator = pass_config.get('generator')
            if not generator:
                raise ValueError("Generator pass has no generator")
                
            self._apply_generator(file_obj, size, generator, pass_config.get('params', {}))
            
        else:
            raise ValueError(f"Unknown pass type: {pass_type}")
    
    def _apply_generator(self, file_obj, size: int, generator: str, params: Dict) -> None:
        """
        Apply a pattern using a generator.
        
        Args:
            file_obj: File object to write to
            size: Size of the file in bytes
            generator: Name of the generator to use
            params: Parameters for the generator
        """
        if generator == 'random':
            # Generate random data
            self._write_random_data(file_obj, size)
            
        elif generator == 'zeros':
            # Generate all zeros
            self._write_pattern(file_obj, b'\x00', size)
            
        elif generator == 'ones':
            # Generate all ones
            self._write_pattern(file_obj, b'\xFF', size)
            
        elif generator == 'alternating':
            # Generate alternating pattern
            alt_type = params.get('type', 'bits')
            
            if alt_type == 'bits':
                # Alternating bits: 0101...
                pattern = bytes([0x55])
            elif alt_type == 'bytes':
                # Alternating bytes: 00FF00FF...
                pattern = b'\x00\xFF'
            else:
                # Default to alternating bits
                pattern = bytes([0x55])
                
            self._write_pattern(file_obj, pattern, size)
            
        elif generator == 'random_complement':
            # Generate random data followed by its complement
            # Seek to beginning of file
            file_obj.seek(0)
            
            # First half is random
            half_size = size // 2
            self._write_random_data(file_obj, half_size)
            
            # Read back the first half
            file_obj.seek(0)
            first_half = file_obj.read(half_size)
            
            # Generate complement
            complement = bytes([~b & 0xFF for b in first_half])
            
            # Write complement
            file_obj.seek(half_size)
            file_obj.write(complement)
            
            # Pad with random if needed
            remaining = size - (half_size * 2)
            if remaining > 0:
                file_obj.seek(half_size * 2)
                file_obj.write(os.urandom(remaining))
                
        elif generator == 'ascii_noise':
            # Generate random printable ASCII characters
            # Printable ASCII range: 32-126
            chunk_size = min(1024 * 1024, size)  # 1 MB chunks or file size if smaller
            
            # Generate chunk of random printable ASCII
            ascii_bytes = bytes([random.randint(32, 126) for _ in range(chunk_size)])
            
            # Write in chunks
            bytes_written = 0
            
            while bytes_written < size:
                # Last chunk might be smaller
                if bytes_written + len(ascii_bytes) > size:
                    chunk = ascii_bytes[:size - bytes_written]
                else:
                    chunk = ascii_bytes
                
                # Write the chunk
                file_obj.write(chunk)
                
                # Flush to disk
                file_obj.flush()
                os.fsync(file_obj.fileno())
                
                bytes_written += len(chunk)
                
        elif generator == 'fibonacci':
            # Generate Fibonacci sequence as a byte pattern
            # Start with 0, 1
            a, b = 0, 1
            
            # Generate sequence up to 255
            fibonacci_bytes = []
            while a <= 255 and len(fibonacci_bytes) < 255:
                fibonacci_bytes.append(a)
                a, b = b, (a + b) % 256  # Keep values in byte range
                
            # Convert to bytes
            pattern = bytes(fibonacci_bytes)
            
            # Write pattern
            self._write_pattern(file_obj, pattern, size)
            
        elif generator == 'counter':
            # Generate incrementing counter pattern
            chunk_size = min(1024 * 1024, size)  # 1 MB chunks or file size if smaller
            
            # Generate counter bytes
            counter_bytes = bytes([(i % 256) for i in range(chunk_size)])
            
            # Write in chunks
            bytes_written = 0
            
            while bytes_written < size:
                # Last chunk might be smaller
                if bytes_written + len(counter_bytes) > size:
                    chunk = counter_bytes[:size - bytes_written]
                else:
                    chunk = counter_bytes
                
                # Write the chunk
                file_obj.write(chunk)
                
                # Flush to disk
                file_obj.flush()
                os.fsync(file_obj.fileno())
                
                bytes_written += len(chunk)
                
        elif generator == 'random_blocks':
            # Generate random blocks of data with random sizes
            # Define minimum and maximum block sizes
            min_block = params.get('min_block', 512)
            max_block = params.get('max_block', 8192)
            
            bytes_written = 0
            
            while bytes_written < size:
                # Generate random block size
                block_size = random.randint(min_block, max_block)
                
                # Last block might be smaller
                if bytes_written + block_size > size:
                    block_size = size - bytes_written
                
                # Generate and write random block
                file_obj.write(os.urandom(block_size))
                
                # Flush to disk
                file_obj.flush()
                os.fsync(file_obj.fileno())
                
                bytes_written += block_size
                
        else:
            raise ValueError(f"Unknown generator: {generator}")
    
    def _write_random_data(self, file_obj, size: int) -> None:
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
    
    def _write_pattern(self, file_obj, pattern: bytes, size: int) -> None:
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