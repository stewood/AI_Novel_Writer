"""
Configuration modules for the NovelWriter Idea Generator.

This package contains configuration-related modules used throughout the application:

- llm: Configuration for LLM integration, including API key management and client creation
- logging: Logging setup and custom log levels including SUPERDEBUG for detailed tracing
"""

from .logging import setup_logging, get_logger

__all__ = ['setup_logging', 'get_logger'] 