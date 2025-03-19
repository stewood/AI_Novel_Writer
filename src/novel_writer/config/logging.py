"""Logging configuration for the Novel Writer package.

This module provides logging configuration with custom log levels and handlers.
It includes a custom SUPERDEBUG level for extremely detailed logging beyond
the standard DEBUG level, useful for tracing every function call and LLM interaction.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Custom log level for super detailed debugging
SUPERDEBUG = 5
logging.addLevelName(SUPERDEBUG, "SUPERDEBUG")

def superdebug(self, message, *args, **kwargs):
    """Log a message at the SUPERDEBUG level.
    
    This custom log level is used for extremely detailed logging that would be
    too verbose even for DEBUG level, such as prompt contents, LLM responses,
    and internal function call details.
    
    Args:
        message: The message to log
        *args: Variable arguments for the message
        **kwargs: Keyword arguments for the logger
    """
    if self.isEnabledFor(SUPERDEBUG):
        self._log(SUPERDEBUG, message, args, **kwargs)

logging.Logger.superdebug = superdebug

def setup_logging(level=logging.INFO, log_file=None, console=True):
    """Configure logging with custom levels and handlers.
    
    Args:
        level: Logging level (e.g., logging.INFO, SUPERDEBUG)
        log_file: Path to the log file (str or Path). If None, a default path in the logs directory is used.
        console: Whether to also log to console
        
    Returns:
        The configured logger
    """
    # Convert string level names to numeric levels
    if isinstance(level, str):
        if level == "SUPERDEBUG":
            level = SUPERDEBUG
        else:
            level = getattr(logging, level, logging.INFO)
    
    # Create logs directory if it doesn't exist
    if log_file is None:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = logs_dir / f"novelwriter_{timestamp}.log"
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Add file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Log initialization
    root_logger.info(f"Logging initialized at level {logging.getLevelName(level)}")
    root_logger.info(f"Log file: {log_file.absolute()}")
    
    return root_logger

def get_logger(name):
    """Get a logger with the specified name.
    
    Args:
        name: The name for the logger
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name) 