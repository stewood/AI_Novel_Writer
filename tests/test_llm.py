"""Test script for LLM configuration and basic functionality."""

import os
import logging
from pathlib import Path

from novel_writer.config.llm import LLMConfig
from novel_writer.config.logging import setup_logging, SUPERDEBUG

def test_llm_basic():
    """Test basic LLM functionality with SUPERDEBUG logging."""
    # Set up logging
    setup_logging(
        level=SUPERDEBUG,
        log_file="logs/llm_test.log",
        console=True
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Get API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        logger.info("Initializing LLM configuration")
        llm_config = LLMConfig(api_key=api_key)
        
        # Test prompt
        test_prompt = """Generate a story concept for a cozy fantasy novel.
        Format your response as JSON:
        {
            "title": "a catchy title",
            "setting": "detailed setting description",
            "main_character": "brief character description",
            "conflict": "main story conflict",
            "tone": "emotional tone",
            "themes": ["theme 1", "theme 2", "theme 3"]
        }
        """
        
        logger.info("Sending test prompt to LLM")
        response = llm_config.get_completion(test_prompt)
        
        logger.info("Successfully received response from LLM")
        logger.info(f"Response: {response}")
        
    except Exception as e:
        logger.error(f"Error during LLM test: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    test_llm_basic() 