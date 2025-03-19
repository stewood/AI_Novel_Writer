"""Tests for the PitchGeneratorAgent class."""

import os
import asyncio
import logging
import json
import pytest
from unittest.mock import MagicMock, patch

from novel_writer.agents.pitch_generator_agent import PitchGeneratorAgent
from novel_writer.config.llm import LLMConfig


@pytest.fixture
def mock_llm_config():
    """Create a mock LLM config."""
    return MagicMock(spec=LLMConfig)


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return MagicMock(spec='Logger')


@pytest.fixture
def sample_pitches_response():
    """Create a sample pitches response."""
    return {
        "pitches": [
            {
                "title": "Quantum Dreams",
                "hook": "A quantum physicist discovers that dreams are actually glimpses into parallel universes.",
                "premise": "Dr. Elena Reyes, a brilliant quantum physicist, discovers that consciousness can traverse the multiverse during sleep. As she begins to map these parallel realities, she realizes one universe threatens to collapse into hers.",
                "main_conflict": "Elena must navigate increasingly unstable connections between universes as she attempts to prevent a catastrophic collapse while government agencies and rival scientists pursue her research for their own purposes.",
                "twist": "The protagonist realizes they are actually dreaming in all the other universes, and this world is the dream."
            }
        ]
    }

def test_pitch_generator_agent_initialization(mock_llm_config):
    """Test Pitch Generator Agent initialization."""
    # Patch the logging function to avoid needing the logger param
    with patch('src.novel_writer.agents.pitch_generator_agent.logger'):
        agent = PitchGeneratorAgent(llm_config=mock_llm_config)
        assert agent.llm_config == mock_llm_config

@pytest.mark.asyncio
async def test_generate_pitches(mock_llm_config, sample_pitches_response):
    """Test pitch generation."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_pitches_response)
    
    # Initialize the agent
    with patch('src.novel_writer.agents.pitch_generator_agent.logger'):
        agent = PitchGeneratorAgent(llm_config=mock_llm_config)
        
        # Call the method
        pitches = await agent.generate_pitches(
            genre="Science Fiction",
            subgenre="Cyberpunk",
            tone="Gritty",
            themes=["Technology", "Identity", "Control"]
        )
        
        # Assertions
        assert len(pitches) == 1
        assert pitches[0]["title"] == "Quantum Dreams"
        assert "hook" in pitches[0]
        assert "premise" in pitches[0]
        assert "main_conflict" in pitches[0]
        assert "twist" in pitches[0] or "unique_twist" in pitches[0]
        
        # Verify the LLM was called with an appropriate prompt
        mock_llm_config.get_completion.assert_called_once()
        prompt = mock_llm_config.get_completion.call_args[0][0]
        assert "Cyberpunk" in prompt
        assert "Science Fiction" in prompt
        assert "Gritty" in prompt
        assert "Technology" in prompt
        assert "Identity" in prompt
        assert "Control" in prompt

@pytest.mark.asyncio
async def test_generate_pitches_error_handling(mock_llm_config):
    """Test error handling in pitch generation."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    with patch('src.novel_writer.agents.pitch_generator_agent.logger'):
        agent = PitchGeneratorAgent(llm_config=mock_llm_config)
        
        # Call the method and expect an exception
        with pytest.raises(Exception) as excinfo:
            await agent.generate_pitches(
                genre="Science Fiction",
                subgenre="Cyberpunk",
                tone="Gritty",
                themes=["Technology", "Identity", "Control"]
            )
            
        # Verify the exception message
        assert "Error getting LLM response" in str(excinfo.value) 