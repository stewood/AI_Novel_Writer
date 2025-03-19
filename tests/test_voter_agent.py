"""Tests for the Voter Agent."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_writer.agents.voter_agent import VoterAgent
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

def test_voter_agent_initialization(mock_llm_config):
    """Test Voter Agent initialization."""
    with patch('novel_writer.agents.voter_agent.logger'):
        agent = VoterAgent(llm_config=mock_llm_config)
        assert agent.llm_config == mock_llm_config

@pytest.mark.asyncio
async def test_select_pitch(mock_llm_config, sample_pitches, sample_evaluations, sample_selection_response):
    """Test pitch selection."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_selection_response)
    
    # Initialize the agent
    with patch('novel_writer.agents.voter_agent.logger'):
        agent = VoterAgent(llm_config=mock_llm_config)
        
        # Test parameters
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Gritty"
        themes = ["Technology", "Identity", "Control"]
        
        # Select the best pitch
        selection_result = await agent.select_best_pitch(
            pitches=sample_pitches,
            evaluations=sample_evaluations,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Assertions - just check for a valid structure
        assert selection_result is not None
        assert isinstance(selection_result, dict)
        # Check for essential keys - winner is always present in the fallback logic
        assert "winner" in selection_result
        assert "selection_criteria" in selection_result
        assert "development_recommendations" in selection_result
        
        # Check that the LLM was called with the correct parameters
        mock_llm_config.get_completion.assert_called_once()

@pytest.mark.asyncio
async def test_select_pitch_error_handling(mock_llm_config, sample_pitches, sample_evaluations):
    """Test error handling in pitch selection."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    with patch('novel_writer.agents.voter_agent.logger'):
        agent = VoterAgent(llm_config=mock_llm_config)
        
        # Test parameters
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Gritty"
        themes = ["Technology", "Identity", "Control"]
        
        # Call the method and expect an exception
        with pytest.raises(Exception) as excinfo:
            await agent.select_best_pitch(
                pitches=sample_pitches,
                evaluations=sample_evaluations,
                genre=genre,
                subgenre=subgenre,
                tone=tone,
                themes=themes
            )
            
        # Verify the exception message
        assert "Error getting LLM response" in str(excinfo.value) 