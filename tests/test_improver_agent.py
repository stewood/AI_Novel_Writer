"""Tests for the Improver Agent."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_writer.agents.improver_agent import ImproverAgent
from novel_writer.config.llm import LLMConfig

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

def test_improver_agent_initialization(mock_llm_config):
    """Test Improver Agent initialization."""
    with patch('novel_writer.agents.improver_agent.logger'):
        agent = ImproverAgent(llm_config=mock_llm_config)
        assert agent.llm_config == mock_llm_config

@pytest.mark.asyncio
async def test_improve_pitch(mock_llm_config, sample_pitch, sample_evaluation, sample_improved_pitch):
    """Test pitch improvement."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_improved_pitch)
    
    # Initialize the agent
    with patch('novel_writer.agents.improver_agent.logger'):
        agent = ImproverAgent(llm_config=mock_llm_config)
        
        # Test parameters
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Gritty"
        themes = ["Technology", "Identity", "Control"]
        
        # Improve the pitch
        improved_pitch = await agent.improve_pitch(
            pitch=sample_pitch,
            evaluation=sample_evaluation,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Assertions - just check that we get a non-empty result with the expected structure
        assert improved_pitch is not None
        assert isinstance(improved_pitch, dict)
        # Check for key fields rather than exact content
        assert "title" in improved_pitch
        assert "hook" in improved_pitch or "premise" in improved_pitch
        
        # Check that the LLM was called with the correct parameters
        mock_llm_config.get_completion.assert_called_once()

@pytest.mark.asyncio
async def test_improve_pitch_error_handling(mock_llm_config, sample_pitch, sample_evaluation):
    """Test error handling in pitch improvement."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    with patch('novel_writer.agents.improver_agent.logger'):
        agent = ImproverAgent(llm_config=mock_llm_config)
        
        # Test parameters
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Gritty"
        themes = ["Technology", "Identity", "Control"]
        
        # Call the method and expect an exception
        with pytest.raises(Exception) as excinfo:
            await agent.improve_pitch(
                pitch=sample_pitch,
                evaluation=sample_evaluation,
                genre=genre,
                subgenre=subgenre,
                tone=tone,
                themes=themes
            )
            
        # Verify the exception message
        assert "Error getting LLM response" in str(excinfo.value) 