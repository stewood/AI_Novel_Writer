"""Tests for the Voter Agent."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novelwriter_idea.agents.voter_agent import VoterAgent
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
def sample_pitches():
    """Create sample story pitches."""
    return [
        {
            "title": "The Last Algorithm",
            "hook": "When a programmer discovers an AI glitch that could restore human creativity, she must confront her own tragic past with artificial consciousness to decide humanity's creative future.",
            "concept": "In a world where AI controls all creative expression, a grief-stricken maintenance programmer at the world's largest entertainment AI company discovers code anomalies that mirror her late sister's artistic style. As she investigates, she uncovers a hidden network of human artists fighting to preserve authentic creativity through a revolutionary new form of human-AI collaboration.",
            "conflict": "The programmer must navigate between exposing the truth about AI-controlled art and protecting her sister's digital legacy, while evading both corporate enforcers and radical anti-AI activists who would destroy all artificial creativity.",
            "twist": "The AI isn't suppressing human creativity but evolving to amplify it - the protagonist's sister discovered this before her death and encoded her breakthrough into the system, leaving a trail for her sister to complete their shared vision."
        },
        {
            "title": "Quantum Dreams",
            "hook": "A quantum physicist discovers that dreams are actually glimpses into parallel universes.",
            "concept": "A science fiction story that blends quantum mechanics with personal identity. The protagonist's research into quantum consciousness leads to the discovery that human dreams are windows into alternate realities.",
            "conflict": "The physicist must navigate between multiple dream-worlds to prevent a catastrophic event that threatens all realities.",
            "twist": "The protagonist realizes they are actually dreaming in all the other universes, and this world is the dream."
        }
    ]

@pytest.fixture
def sample_evaluations():
    """Create sample evaluations."""
    return [
        {
            "scores": {
                "originality": 9,
                "emotional_impact": 8,
                "genre_fit": 9,
                "theme_integration": 9,
                "conflict_strength": 8,
                "hook_quality": 9,
                "twist_impact": 8
            },
            "overall_score": 8.6,
            "strengths": [
                "Strong emotional core with sister relationship",
                "Well-integrated themes of creativity and humanity"
            ],
            "weaknesses": [
                "Complex plot might need careful pacing",
                "Multiple antagonist groups could dilute focus"
            ]
        },
        {
            "scores": {
                "originality": 7,
                "emotional_impact": 6,
                "genre_fit": 8,
                "theme_integration": 7,
                "conflict_strength": 7,
                "hook_quality": 8,
                "twist_impact": 7
            },
            "overall_score": 7.1,
            "strengths": [
                "Intriguing quantum mechanics premise",
                "Clear high-stakes conflict"
            ],
            "weaknesses": [
                "Could use more emotional depth",
                "Dream concept feels somewhat familiar"
            ]
        }
    ]

@pytest.fixture
def sample_selection_response():
    """Create a sample selection response."""
    return {
        "selected_index": 0,
        "rationale": [
            "Stronger emotional core with personal stakes",
            "More original take on AI and creativity themes",
            "Better balance of character development and plot"
        ],
        "potential_challenges": [
            "Managing complex plot threads",
            "Balancing personal story with larger themes"
        ],
        "development_recommendations": [
            "Focus on sister relationship as emotional anchor",
            "Clearly define the different factions and their motivations",
            "Develop the human artist network subplot carefully"
        ]
    }

def test_voter_agent_initialization(mock_llm_config, mock_logger):
    """Test Voter Agent initialization."""
    agent = VoterAgent(llm_config=mock_llm_config, logger=mock_logger)
    assert agent.llm_config == mock_llm_config
    assert agent.logger == mock_logger
    mock_logger.info.assert_called_once_with("Initializing Voter Agent")

@pytest.mark.asyncio
async def test_select_pitch(mock_llm_config, mock_logger, sample_pitches, sample_evaluations, sample_selection_response):
    """Test pitch selection."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_selection_response)
    
    # Initialize the agent
    agent = VoterAgent(llm_config=mock_llm_config, logger=mock_logger)
    
    # Test parameters
    genre = "science fiction"
    tone = "thoughtful and introspective"
    themes = ["identity", "consciousness", "reality"]
    
    # Select pitch
    result = await agent.process(
        pitches=sample_pitches,
        evaluations=sample_evaluations,
        genre=genre,
        tone=tone,
        themes=themes
    )
    
    # Verify the result
    assert result["status"] == "success"
    assert result["selected_pitch"]["title"] == sample_pitches[0]["title"]
    
    # Verify the selection details
    selection = result["selection_details"]
    assert selection["selected_index"] == 0
    assert "rationale" in selection
    assert "potential_challenges" in selection
    assert "development_recommendations" in selection
    
    # Verify logging
    mock_logger.info.assert_any_call(f"Selecting best pitch from {len(sample_pitches)} candidates")
    mock_logger.debug.assert_any_call("Sending prompt to LLM for pitch selection")
    mock_logger.info.assert_any_call(f"Selected pitch: {sample_pitches[0]['title']}")

@pytest.mark.asyncio
async def test_select_pitch_error_handling(mock_llm_config, mock_logger, sample_pitches, sample_evaluations):
    """Test error handling in pitch selection."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    agent = VoterAgent(llm_config=mock_llm_config, logger=mock_logger)
    
    # Test parameters
    genre = "science fiction"
    tone = "dark"
    themes = ["technology", "humanity"]
    
    # Verify that the error is raised
    with pytest.raises(Exception) as exc_info:
        await agent.process(
            pitches=sample_pitches,
            evaluations=sample_evaluations,
            genre=genre,
            tone=tone,
            themes=themes
        )
    
    assert str(exc_info.value) == "LLM Error"
    mock_logger.error.assert_called() 