import logging
import os
from datetime import datetime
from pathlib import Path

# Custom log level for super detailed debugging
SUPERDEBUG = 5
logging.addLevelName(SUPERDEBUG, "SUPERDEBUG")

def superdebug(self, message, *args, **kwargs):
    if self.isEnabledFor(SUPERDEBUG):
        self._log(SUPERDEBUG, message, args, **kwargs)

logging.Logger.superdebug = superdebug

def setup_logging(log_level=logging.INFO, log_file=None):
    """Configure logging with custom levels and handlers."""
    if log_file is None:
        log_file = Path("logs/novelwriter.log")
    
    # Create logs directory if it doesn't exist
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_logger(name):
    """Get a logger instance with the specified name."""
    return logging.getLogger(name) 