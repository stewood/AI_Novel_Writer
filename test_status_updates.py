#!/usr/bin/env python
"""Test script for status updates without console logging.

This script simulates the behavior of the status update mechanism
while keeping detailed logs in a file only.
"""

import sys
import logging
import time
from pathlib import Path
from src.novelwriter_idea.config.logging import setup_logging, SUPERDEBUG

# Get the root logger first
logger = logging.getLogger()

# Setup logging - no console output, but file logging enabled
setup_logging(
    level=SUPERDEBUG,  # Use SUPERDEBUG to capture everything
    console=False,     # This is key - no console logging
    log_file="logs/test_status_updates.log"
)

# Get a script-specific logger
script_logger = logging.getLogger(__name__)

# Create a print_status function similar to the one in cli.py
def print_status(message: str, emoji: str = "📝") -> None:
    """Print a status message to the console regardless of console logging setting."""
    if emoji:
        print(f"\n{emoji} {message}")
    else:
        print(f"\n{message}")
    
    # Also log this message at INFO level
    script_logger.info(message)

def main():
    """Run a simple test of status updates."""
    print("\nStarting status update test...\n")
    print("You should see status messages in the console")
    print("but detailed logs will ONLY be in the log file")
    print("logs/test_status_updates.log\n")
    
    # Log some messages at different levels
    script_logger.info("This is an INFO message that should be in the log file ONLY")
    script_logger.debug("This is a DEBUG message that should be in the log file ONLY")
    
    # Print status messages that should always appear in console
    print_status("Initializing test...", "🚀")
    
    # Simulate some processing
    for i in range(1, 4):
        script_logger.info(f"Processing step {i} (this message should be in log file ONLY)")
        time.sleep(1)
        print_status(f"Completed step {i} of the test", "✅")
    
    # Log an error but show a status message
    script_logger.error("This is an ERROR that should be in the log file ONLY")
    print_status("All steps completed successfully", "🎉")
    
    # Log at SUPERDEBUG level
    script_logger.superdebug("This is a SUPERDEBUG message that should be in the log file ONLY")
    
    print("\nTest completed. Check logs/test_status_updates.log for file logs.")
    
if __name__ == "__main__":
    main() 