"""Utility functions for file operations.

This module provides helper functions for common file operations
used throughout the novel_writer application.
"""

import logging
import os
import re
import string
from pathlib import Path
from typing import Optional

# Initialize logger
logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> Optional[str]:
    """Sanitize a string to make it safe for use as a filename.
    
    Removes invalid characters, collapses whitespace, and ensures
    the filename conforms to operating system constraints.
    
    Args:
        filename: The string to sanitize
        
    Returns:
        A sanitized filename or None if the input is empty/invalid
    """
    if not filename or not isinstance(filename, str):
        logger.warning(f"Invalid filename provided: {filename}")
        return None
        
    logger.debug(f"Sanitizing filename: {filename}")
    
    # Remove invalid characters
    valid_chars = string.ascii_letters + string.digits + ' -_.'
    sanitized = ''.join(c for c in filename if c in valid_chars)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Collapse multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Truncate if too long (common filesystem limits)
    max_length = 100  # Safe for most filesystems
    if len(sanitized) > max_length:
        logger.debug(f"Truncating filename from {len(sanitized)} to {max_length} characters")
        sanitized = sanitized[:max_length]
    
    # Remove leading/trailing special characters
    sanitized = sanitized.strip('._-')
    
    # If empty after sanitization, return None
    if not sanitized:
        logger.warning(f"Filename '{filename}' became empty after sanitization")
        return None
        
    logger.debug(f"Sanitized filename: {sanitized}")
    return sanitized 