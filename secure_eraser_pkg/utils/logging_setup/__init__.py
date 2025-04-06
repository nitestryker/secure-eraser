"""
Logging setup utilities for SecureEraser.
"""

import logging

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Configure logging based on verbosity level and optionally to a file.
    
    Args:
        log_level: Logging level
        log_file: Optional path to log file
        
    Returns:
        Logger instance
    """
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger()
    
    # Clear existing handlers to avoid duplication
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
    
    return logger