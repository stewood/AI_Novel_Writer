"""Test script for LLM configuration and basic functionality."""

import os
import logging
import pytest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path

from novel_writer.config.llm import LLMConfig
from novel_writer.config.logging import setup_logging, SUPERDEBUG

@pytest.fixture
def mock_llm_config():
    """Create a mock LLM configuration."""
    config = MagicMock(spec=LLMConfig)
    return config

@pytest.mark.asyncio
async def test_llm_basic(mock_llm_config):
    """Test basic LLM functionality with SUPERDEBUG logging."""
    # Set up logging
    setup_logging(
        level=SUPERDEBUG,
        log_file="logs/llm_test.log",
        console=True
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Mock response
        mock_response = {
            "title": "The Enchanted Teacup",
            "setting": "A cozy village where magic is as common as tea",
            "main_character": "A retired wizard who runs a tea shop",
            "conflict": "A mysterious illness affecting magical plants",
            "tone": "Warm and whimsical",
            "themes": ["Community", "Magic", "Healing"]
        }
        
        # Set up mock to return our test response
        mock_llm_config.get_completion.return_value = json.dumps(mock_response)
        
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
        response = await mock_llm_config.get_completion(test_prompt)
        
        # Verify the response
        assert response == json.dumps(mock_response)
        mock_llm_config.get_completion.assert_called_once_with(test_prompt)
        
        logger.info("Successfully received response from LLM")
        logger.info(f"Response: {response}")
        
    except Exception as e:
        logger.error(f"Error during LLM test: {e}", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_llm_error_handling(mock_llm_config):
    """Test LLM error handling."""
    # Set up mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("API Error")
    
    with pytest.raises(Exception) as exc_info:
        await mock_llm_config.get_completion("test prompt")
    
    assert str(exc_info.value) == "API Error"
    mock_llm_config.get_completion.assert_called_once_with("test prompt")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_llm_basic(MagicMock(spec=LLMConfig))) 