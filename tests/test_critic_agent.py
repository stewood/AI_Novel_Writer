"""Tests for the CriticAgent class."""

import json
import pytest
from unittest.mock import MagicMock, patch

from src.novel_writer.agents.critic_agent import CriticAgent
from src.novel_writer.config.llm import LLMConfig

@pytest.fixture
def mock_llm_config():
    """Create a mock LLM config."""
    return MagicMock(spec=LLMConfig)

@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return MagicMock(spec='Logger')

@pytest.fixture
def sample_pitch():
    """Create a sample pitch."""
    return {
        "title": "The Last Algorithm",
        "hook": "In a world where AI has replaced human creativity, a programmer discovers a glitch that could restore human imagination.",
        "concept": "A near-future thriller where artificial intelligence has become the primary source of entertainment and art. The protagonist, a maintenance programmer for the world's largest entertainment AI, discovers a mysterious anomaly in the code that suggests the AI is hiding something about human creativity.",
        "main_conflict": "The programmer must navigate corporate secrets and rival factions while trying to understand what the AI is hiding about human creative potential.",
        "unique_twist": "The glitch is actually a remnant of human consciousness that was uploaded to the AI network years ago, fighting to be heard."
    }

@pytest.fixture
def sample_evaluation_response():
    """Create a sample evaluation response."""
    return {
        "scores": {
            "originality": 7,
            "emotional_impact": 6,
            "genre_fit": 8,
            "theme_integration": 8,
            "commercial_potential": 7,
            "hook_quality": 8,
            "overall_score": 7.3
        },
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

def test_critic_agent_initialization(mock_llm_config):
    """Test Critic Agent initialization."""
    # Patch the logging function to avoid needing the logger param
    with patch('src.novel_writer.agents.critic_agent.logger'):
        agent = CriticAgent(llm_config=mock_llm_config)
        assert agent.llm_config == mock_llm_config

@pytest.mark.asyncio
async def test_evaluate_pitch(mock_llm_config, sample_pitch, sample_evaluation_response):
    """Test pitch evaluation."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_evaluation_response)
    
    # Initialize the agent
    with patch('src.novel_writer.agents.critic_agent.logger'):
        agent = CriticAgent(llm_config=mock_llm_config)
        
        # Test parameters
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Gritty"
        themes = ["Technology", "Identity", "Control"]
        
        # Evaluate the pitch
        evaluation = await agent.evaluate_pitches(
            pitches=[sample_pitch],
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Assertions
        assert len(evaluation) == 1
        first_eval = evaluation[0]
        assert "scores" in first_eval
        assert "key_strengths" in first_eval
        assert "areas_for_improvement" in first_eval
        assert len(first_eval["scores"]) > 0
        assert len(first_eval["key_strengths"]) > 0
        assert len(first_eval["areas_for_improvement"]) > 0
        
        # Verify the LLM was called with an appropriate prompt
        mock_llm_config.get_completion.assert_called_once()
        prompt = mock_llm_config.get_completion.call_args[0][0]
        assert "Science Fiction" in prompt
        assert "Cyberpunk" in prompt
        assert "Gritty" in prompt
        assert "Technology" in prompt
        assert "The Last Algorithm" in prompt

@pytest.mark.asyncio
async def test_evaluate_pitch_error_handling(mock_llm_config, sample_pitch):
    """Test error handling in pitch evaluation."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    with patch('src.novel_writer.agents.critic_agent.logger'):
        agent = CriticAgent(llm_config=mock_llm_config)
        
        # Test parameters
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Gritty"
        themes = ["Technology", "Identity", "Control"]
        
        # Call the method and expect an exception
        with pytest.raises(Exception) as excinfo:
            await agent.evaluate_pitches(
                pitches=[sample_pitch],
                genre=genre,
                subgenre=subgenre,
                tone=tone,
                themes=themes
            )
            
        # Verify the exception message
        assert "Error getting LLM response" in str(excinfo.value) 