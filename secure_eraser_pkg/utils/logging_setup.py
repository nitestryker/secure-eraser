"""
Logging configuration for the Secure Eraser tool.
"""

import logging
import sys
from typing import Optional


def setup_logging(log_level=logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure logging based on verbosity level and optionally to a file
    
    Args:
        log_level: Logging level (logging.DEBUG, logging.INFO, etc.)
        log_file: Path to save log file (if None, logs will only be shown on console)
        
    Returns:
        Logger instance configured with the specified settings
    """
    # Create logger
    logger = logging.getLogger("secure_eraser")
    logger.setLevel(log_level)
    logger.handlers = []  # Clear existing handlers
    
    # Log format with timestamp
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # File handler if a log file is specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to create log file {log_file}: {e}")
    
    return logger