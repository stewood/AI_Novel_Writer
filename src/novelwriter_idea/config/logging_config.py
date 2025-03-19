"""Logging configuration for novelwriter_idea."""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

# Custom log level for super detailed debugging
SUPERDEBUG = 5
logging.addLevelName(SUPERDEBUG, "SUPERDEBUG")

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    rich_traceback: bool = True
) -> None:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (ERROR, WARN, INFO, DEBUG, SUPERDEBUG)
        log_file: Path to log file. If None, only logs to console
        console_output: Whether to output logs to console
        rich_traceback: Whether to use rich tracebacks in console output
    """
    # Convert string level to numeric value
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        if log_level.upper() == "SUPERDEBUG":
            numeric_level = SUPERDEBUG
        else:
            raise ValueError(f"Invalid log level: {log_level}")
    
    # Create logs directory if logging to file
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Base configuration
    config = {
        "level": numeric_level,
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "handlers": []
    }
    
    # Add console handler if requested
    if console_output:
        console = Console(force_terminal=True)
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=rich_traceback,
            markup=True,
            show_time=False
        )
        console_handler.setLevel(numeric_level)
        config["handlers"].append(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        formatter = logging.Formatter(config["format"], config["datefmt"])
        file_handler.setFormatter(formatter)
        config["handlers"].append(file_handler)
    
    # Apply configuration
    logging.basicConfig(**config)
    
    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Create logger for our package
    logger = logging.getLogger("novelwriter_idea")
    logger.setLevel(numeric_level)
    
    # Log initial setup
    logger.info(f"Logging initialized at level {log_level}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")
    
def log_superdebug(self, message, *args, **kwargs):
    """Log at SUPERDEBUG level."""
    if self.isEnabledFor(SUPERDEBUG):
        self._log(SUPERDEBUG, message, args, **kwargs)

# Add superdebug method to Logger class
logging.Logger.superdebug = log_superdebug 