"""Logging configuration for novelwriter_idea."""

import logging
import sys
import warnings
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

# Import main logging setup function
from .logging import setup_logging as main_setup_logging, SUPERDEBUG

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    rich_traceback: bool = True
) -> None:
    """Set up logging configuration.
    
    This is a compatibility function that forwards to the main logging setup function.
    
    Args:
        log_level: Logging level (ERROR, WARN, INFO, DEBUG, SUPERDEBUG)
        log_file: Path to log file. If None, a default with timestamp will be used.
        console_output: Whether to output logs to console
        rich_traceback: Whether to use rich tracebacks in console output (ignored)
    """
    # Show deprecation warning
    warnings.warn(
        "This logging_config module is deprecated. Use novelwriter_idea.config.logging directly.", 
        DeprecationWarning, 
        stacklevel=2
    )
    
    # Convert string level to numeric value
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        if log_level.upper() == "SUPERDEBUG":
            numeric_level = SUPERDEBUG
        else:
            raise ValueError(f"Invalid log level: {log_level}")
    
    # Forward to main setup function
    main_setup_logging(
        level=numeric_level,
        log_file=log_file,
        console=console_output
    )

def log_superdebug(self, message, *args, **kwargs):
    """Log at SUPERDEBUG level."""
    if self.isEnabledFor(SUPERDEBUG):
        self._log(SUPERDEBUG, message, args, **kwargs)

# Add superdebug method to Logger class
logging.Logger.superdebug = log_superdebug 