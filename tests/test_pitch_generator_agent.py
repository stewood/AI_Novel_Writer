"""Tests for the Pitch Generator Agent."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novelwriter_idea.agents.pitch_generator_agent import PitchGeneratorAgent
from novelwriter_idea.config.llm import LLMConfig

@pytest.fixture
def mock_llm_config():
    """Create a mock LLM configuration."""
    return MagicMock(spec=LLMConfig)

@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return MagicMock(spec=logging.Logger)

@pytest.fixture
def sample_pitches_response():
    """Create a sample pitches response."""
    return {
        "pitches": [
            {
                "title": "The Last Algorithm",
                "hook": "In a world where AI has replaced human creativity, a programmer discovers a glitch that could restore human imagination.",
                "concept": "A near-future thriller where artificial intelligence has become the primary source of entertainment and art. The protagonist, a maintenance programmer for the world's largest entertainment AI, discovers a mysterious anomaly in the code that suggests the AI is hiding something about human creativity.",
                "conflict": "The programmer must choose between reporting the glitch and potentially losing their job, or investigating further and risking exposure to dangerous corporate secrets.",
                "twist": "The glitch is actually a remnant of human consciousness that was uploaded to the AI network years ago, fighting to be heard."
            },
            {
                "title": "Quantum Dreams",
                "hook": "A quantum physicist discovers that dreams are actually glimpses into parallel universes.",
                "concept": "A science fiction story that blends quantum mechanics with personal identity. The protagonist's research into quantum consciousness leads to the discovery that human dreams are windows into alternate realities.",
                "conflict": "The physicist must navigate between multiple dream-worlds to prevent a catastrophic event that threatens all realities.",
                "twist": "The protagonist realizes they are actually dreaming in all the other universes, and this world is the dream."
            }
        ]
    }

def test_pitch_generator_agent_initialization(mock_llm_config, mock_logger):
    """Test Pitch Generator Agent initialization."""
    agent = PitchGeneratorAgent(llm_config=mock_llm_config, logger=mock_logger)
    assert agent.llm_config == mock_llm_config
    assert agent.logger == mock_logger
    mock_logger.info.assert_called_once_with("Initializing Pitch Generator Agent")

@pytest.mark.asyncio
async def test_generate_pitches(mock_llm_config, mock_logger, sample_pitches_response):
    """Test pitch generation."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_pitches_response)
    
    # Initialize the agent
    agent = PitchGeneratorAgent(llm_config=mock_llm_config, logger=mock_logger)
    
    # Test parameters
    genre = "science fiction"
    tone = "thoughtful and introspective"
    themes = ["identity", "consciousness", "reality"]
    
    # Generate pitches
    result = await agent.process(genre=genre, tone=tone, themes=themes)
    
    # Verify the result
    assert result["status"] == "success"
    assert result["num_pitches"] == 2
    assert len(result["pitches"]) == 2
    
    # Verify the first pitch
    first_pitch = result["pitches"][0]
    assert "title" in first_pitch
    assert "hook" in first_pitch
    assert "concept" in first_pitch
    assert "conflict" in first_pitch
    assert "twist" in first_pitch
    
    # Verify logging
    mock_logger.info.assert_any_call(f"Generating 3 pitches for {genre} story")
    mock_logger.debug.assert_any_call("Sending prompt to LLM for pitch generation")
    mock_logger.info.assert_any_call("Successfully generated 2 pitches")

@pytest.mark.asyncio
async def test_generate_pitches_error_handling(mock_llm_config, mock_logger):
    """Test error handling in pitch generation."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    agent = PitchGeneratorAgent(llm_config=mock_llm_config, logger=mock_logger)
    
    # Test parameters
    genre = "fantasy"
    tone = "whimsical"
    themes = ["magic", "adventure"]
    
    # Verify that the error is raised
    with pytest.raises(Exception) as exc_info:
        await agent.process(genre=genre, tone=tone, themes=themes)
    
    assert str(exc_info.value) == "LLM Error"
    mock_logger.error.assert_called() 