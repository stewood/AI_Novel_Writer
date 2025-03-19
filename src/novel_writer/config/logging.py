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

def setup_logging(level=logging.INFO, log_file=None, console=True):
    """Configure logging with custom levels and handlers.
    
    Args:
        level: Logging level (e.g., logging.INFO, SUPERDEBUG)
        log_file: Path to the log file (str or Path). If None, a default path in the logs directory is used.
        console: Whether to enable console logging
        
    Returns:
        Configured root logger
    """
    # Always ensure we have a log file
    if log_file is None:
        # Default log file with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = Path(f"logs/novelwriter_{timestamp}.log")
    elif not isinstance(log_file, Path):
        log_file = Path(log_file)
    
    # Create logs directory if it doesn't exist
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler - always add this
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)
    
    # Log the configuration details
    root_logger.info(f"Logging initialized at level {logging.getLevelName(level)}")
    root_logger.info(f"Log file: {log_file.absolute()}")
    if console:
        root_logger.info("Console logging enabled")
    
    return root_logger

def get_logger(name):
    """Get a logger instance with the specified name."""
    return logging.getLogger(name) 