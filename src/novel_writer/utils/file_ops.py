"""Utility functions for file and path operations.

This module provides helper functions for common file and path operations
used throughout the novel_writer application.
"""

import logging
import os
import re
import string
import unicodedata
from pathlib import Path
from typing import Optional, Union

# Initialize logger
logger = logging.getLogger(__name__)

def sanitize_filename(text: str, max_length: int = 100) -> Optional[str]:
    """Sanitize a string to make it safe for use as a filename.
    
    More restrictive than slugify, ensuring the filename is safe across all major
    operating systems. Use this when dealing with actual files.
    
    Args:
        text: The string to sanitize
        max_length: Maximum length for the filename (default 100)
        
    Returns:
        A sanitized filename or None if the input is empty/invalid
    """
    if not text or not isinstance(text, str):
        logger.warning(f"Invalid filename provided: {text}")
        return None
        
    logger.debug(f"Sanitizing filename: {text}")
    
    # Remove invalid characters
    valid_chars = string.ascii_letters + string.digits + ' -_.'
    sanitized = ''.join(c for c in text if c in valid_chars)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Collapse multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Truncate if too long
    if len(sanitized) > max_length:
        logger.debug(f"Truncating filename from {len(sanitized)} to {max_length} characters")
        sanitized = sanitized[:max_length]
    
    # Remove leading/trailing special characters
    sanitized = sanitized.strip('._-')
    
    # If empty after sanitization, return None
    if not sanitized:
        logger.warning(f"Text '{text}' became empty after sanitization")
        return None
        
    logger.debug(f"Sanitized filename: {sanitized}")
    return sanitized

def slugify(text: str) -> str:
    """Convert text into a URL and filesystem friendly slug.
    
    Less restrictive than sanitize_filename, allowing hyphens and keeping URL-friendly
    characters. Use this for URLs, directory names, or other web-friendly contexts.
    
    Args:
        text: The text to convert into a slug
        
    Returns:
        A slugified version of the text
    """
    # Convert to lowercase and normalize unicode characters
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    
    # Replace any non-alphanumeric characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    
    return text

def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: The directory path to ensure exists (str or Path)
        
    Returns:
        Path object of the ensured directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_unique_filename(base_path: Union[str, Path], extension: Optional[str] = None) -> Path:
    """Get a unique filename by appending a number if the file already exists.
    
    Args:
        base_path: The base path for the file (str or Path)
        extension: Optional file extension (without the dot)
        
    Returns:
        A Path object with a unique filename
    """
    base_path = Path(base_path)
    
    if extension:
        stem = base_path.stem
        suffix = f".{extension}"
    else:
        stem = base_path.stem
        suffix = base_path.suffix
    
    counter = 1
    result_path = base_path
    
    while result_path.exists():
        result_path = base_path.parent / f"{stem}_{counter}{suffix}"
        counter += 1
    
    return result_path 