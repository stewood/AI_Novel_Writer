"""Tests for the Improver Agent."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novelwriter_idea.agents.improver_agent import ImproverAgent
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
def sample_evaluation():
    """Create a sample evaluation."""
    return {
        "scores": {
            "originality": 6,
            "emotional_impact": 7,
            "genre_fit": 9,
            "theme_integration": 8,
            "conflict_strength": 8,
            "hook_quality": 9,
            "twist_impact": 6
        },
        "overall_score": 7.6,
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

@pytest.fixture
def sample_improved_pitch():
    """Create a sample improved pitch response."""
    return {
        "title": "The Last Algorithm",
        "hook": "When a programmer discovers an AI glitch that could restore human creativity, she must confront her own tragic past with artificial consciousness to decide humanity's creative future.",
        "concept": "In a world where AI controls all creative expression, a grief-stricken maintenance programmer at the world's largest entertainment AI company discovers code anomalies that mirror her late sister's artistic style. As she investigates, she uncovers a hidden network of human artists fighting to preserve authentic creativity through a revolutionary new form of human-AI collaboration.",
        "conflict": "The programmer must navigate between exposing the truth about AI-controlled art and protecting her sister's digital legacy, while evading both corporate enforcers and radical anti-AI activists who would destroy all artificial creativity.",
        "twist": "The AI isn't suppressing human creativity but evolving to amplify it - the protagonist's sister discovered this before her death and encoded her breakthrough into the system, leaving a trail for her sister to complete their shared vision.",
        "improvements_made": [
            "Added personal stakes through sister relationship",
            "Enhanced emotional depth of conflict",
            "Created more nuanced twist about AI-human collaboration",
            "Strengthened originality by avoiding common AI consciousness trope"
        ],
        "elements_preserved": [
            "Core theme of human creativity vs AI",
            "Corporate thriller elements",
            "Programming/tech background",
            "Strong hook concept"
        ]
    }

def test_improver_agent_initialization(mock_llm_config, mock_logger):
    """Test Improver Agent initialization."""
    agent = ImproverAgent(llm_config=mock_llm_config, logger=mock_logger)
    assert agent.llm_config == mock_llm_config
    assert agent.logger == mock_logger
    mock_logger.info.assert_called_once_with("Initializing Improver Agent")

@pytest.mark.asyncio
async def test_improve_pitch(mock_llm_config, mock_logger, sample_pitch, sample_evaluation, sample_improved_pitch):
    """Test pitch improvement."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_improved_pitch)
    
    # Initialize the agent
    agent = ImproverAgent(llm_config=mock_llm_config, logger=mock_logger)
    
    # Test parameters
    genre = "science fiction"
    tone = "thoughtful and introspective"
    themes = ["identity", "consciousness", "reality"]
    
    # Improve pitch
    result = await agent.process(
        pitch=sample_pitch,
        evaluation=sample_evaluation,
        genre=genre,
        tone=tone,
        themes=themes
    )
    
    # Verify the result
    assert result["status"] == "success"
    assert result["original_title"] == sample_pitch["title"]
    
    # Verify the improved pitch
    improved = result["improved_pitch"]
    assert "title" in improved
    assert "hook" in improved
    assert "concept" in improved
    assert "conflict" in improved
    assert "twist" in improved
    assert "improvements_made" in improved
    assert "elements_preserved" in improved
    
    # Verify logging
    mock_logger.info.assert_any_call(f"Improving pitch: {sample_pitch['title']}")
    mock_logger.debug.assert_any_call("Sending prompt to LLM for pitch improvement")
    mock_logger.info.assert_any_call(f"Successfully improved pitch: {improved['title']}")

@pytest.mark.asyncio
async def test_improve_pitch_error_handling(mock_llm_config, mock_logger, sample_pitch, sample_evaluation):
    """Test error handling in pitch improvement."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    agent = ImproverAgent(llm_config=mock_llm_config, logger=mock_logger)
    
    # Test parameters
    genre = "science fiction"
    tone = "dark"
    themes = ["technology", "humanity"]
    
    # Verify that the error is raised
    with pytest.raises(Exception) as exc_info:
        await agent.process(
            pitch=sample_pitch,
            evaluation=sample_evaluation,
            genre=genre,
            tone=tone,
            themes=themes
        )
    
    assert str(exc_info.value) == "LLM Error"
    mock_logger.error.assert_called() 