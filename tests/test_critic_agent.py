"""Tests for the Critic Agent."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novelwriter_idea.agents.critic_agent import CriticAgent
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
def sample_pitch():
    """Create a sample story pitch."""
    return {
        "title": "The Last Algorithm",
        "hook": "In a world where AI has replaced human creativity, a programmer discovers a glitch that could restore human imagination.",
        "concept": "A near-future thriller where artificial intelligence has become the primary source of entertainment and art. The protagonist, a maintenance programmer for the world's largest entertainment AI, discovers a mysterious anomaly in the code that suggests the AI is hiding something about human creativity.",
        "conflict": "The programmer must choose between reporting the glitch and potentially losing their job, or investigating further and risking exposure to dangerous corporate secrets.",
        "twist": "The glitch is actually a remnant of human consciousness that was uploaded to the AI network years ago, fighting to be heard."
    }

@pytest.fixture
def sample_evaluation_response():
    """Create a sample evaluation response."""
    return {
        "scores": {
            "originality": 8,
            "emotional_impact": 7,
            "genre_fit": 9,
            "theme_integration": 8,
            "conflict_strength": 8,
            "hook_quality": 9,
            "twist_impact": 8
        },
        "overall_score": 8.1,
        "strengths": [
            "Strong genre integration with AI and human themes",
            "Compelling hook that immediately draws interest"
        ],
        "weaknesses": [
            "Could develop emotional stakes further",
            "Risk of familiar AI consciousness trope"
        ],
        "improvement_suggestions": [
            "Add personal relationships to increase emotional impact",
            "Consider a more unexpected twist on the AI consciousness angle"
        ]
    }

def test_critic_agent_initialization(mock_llm_config, mock_logger):
    """Test Critic Agent initialization."""
    agent = CriticAgent(llm_config=mock_llm_config, logger=mock_logger)
    assert agent.llm_config == mock_llm_config
    assert agent.logger == mock_logger
    mock_logger.info.assert_called_once_with("Initializing Critic Agent")

@pytest.mark.asyncio
async def test_evaluate_pitch(mock_llm_config, mock_logger, sample_pitch, sample_evaluation_response):
    """Test pitch evaluation."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_evaluation_response)
    
    # Initialize the agent
    agent = CriticAgent(llm_config=mock_llm_config, logger=mock_logger)
    
    # Test parameters
    genre = "science fiction"
    tone = "thoughtful and introspective"
    themes = ["identity", "consciousness", "reality"]
    
    # Evaluate pitch
    result = await agent.process(
        pitches=[sample_pitch],
        genre=genre,
        tone=tone,
        themes=themes
    )
    
    # Verify the result
    assert result["status"] == "success"
    assert len(result["evaluations"]) == 1
    
    # Verify the evaluation
    evaluation = result["evaluations"][0]
    assert evaluation["title"] == sample_pitch["title"]
    assert evaluation["overall_score"] == sample_evaluation_response["overall_score"]
    assert all(score in evaluation["scores"] for score in ["originality", "emotional_impact", "genre_fit"])
    assert "strengths" in evaluation
    assert "weaknesses" in evaluation
    assert "improvement_suggestions" in evaluation
    
    # Verify logging
    mock_logger.info.assert_any_call("Evaluating 1 pitches")
    mock_logger.debug.assert_any_call("Sending prompt to LLM for evaluation")
    mock_logger.info.assert_any_call("Successfully evaluated all pitches")

@pytest.mark.asyncio
async def test_evaluate_pitch_error_handling(mock_llm_config, mock_logger, sample_pitch):
    """Test error handling in pitch evaluation."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    agent = CriticAgent(llm_config=mock_llm_config, logger=mock_logger)
    
    # Test parameters
    genre = "science fiction"
    tone = "dark"
    themes = ["technology", "humanity"]
    
    # Verify that the error is raised
    with pytest.raises(Exception) as exc_info:
        await agent.process(
            pitches=[sample_pitch],
            genre=genre,
            tone=tone,
            themes=themes
        )
    
    assert str(exc_info.value) == "LLM Error"
    mock_logger.error.assert_called() 