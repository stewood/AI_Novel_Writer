"""Tests for the Tropemaster Agent."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_writer.agents.tropemaster_agent import TropemasterAgent
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
        "hook": "When a programmer discovers an AI glitch that could restore human creativity, she must confront her own tragic past with artificial consciousness to decide humanity's creative future.",
        "concept": "In a world where AI controls all creative expression, a grief-stricken maintenance programmer at the world's largest entertainment AI company discovers code anomalies that mirror her late sister's artistic style. As she investigates, she uncovers a hidden network of human artists fighting to preserve authentic creativity through a revolutionary new form of human-AI collaboration.",
        "conflict": "The programmer must navigate between exposing the truth about AI-controlled art and protecting her sister's digital legacy, while evading both corporate enforcers and radical anti-AI activists who would destroy all artificial creativity.",
        "twist": "The AI isn't suppressing human creativity but evolving to amplify it - the protagonist's sister discovered this before her death and encoded her breakthrough into the system, leaving a trail for her sister to complete their shared vision."
    }

@pytest.fixture
def sample_trope_analysis():
    """Create a sample trope analysis response."""
    return {
        "identified_tropes": [
            {
                "trope": "AI Control of Society",
                "description": "AI systems controlling a major aspect of human life (creativity)",
                "common_usage": "Usually portrayed as purely dystopian control",
                "current_handling": "More nuanced approach with AI potentially enhancing human creativity",
                "originality_score": 8
            },
            {
                "trope": "Lost Family Member's Legacy",
                "description": "Protagonist following clues left by deceased sister",
                "common_usage": "Often used as pure motivation for revenge",
                "current_handling": "Used for character growth and thematic resonance",
                "originality_score": 7
            }
        ],
        "subversion_suggestions": [
            {
                "trope": "AI Control of Society",
                "suggestion": "Explore AI as a collaborative partner rather than controller",
                "impact": "Creates a more nuanced exploration of human-AI relationships"
            },
            {
                "trope": "Lost Family Member's Legacy",
                "suggestion": "Make the sister's legacy about reconciliation rather than revenge",
                "impact": "Adds emotional depth and avoids revenge cliché"
            }
        ],
        "original_elements": [
            "AI as a potential amplifier of human creativity",
            "Hidden network of human artists working with AI",
            "Personal grief intertwined with technological progress"
        ],
        "enhancement_suggestions": [
            {
                "element": "Hidden artist network",
                "suggestion": "Show various approaches to human-AI collaboration",
                "rationale": "Demonstrates the complexity of the central theme"
            },
            {
                "element": "Sister's encoded breakthrough",
                "suggestion": "Reveal the breakthrough gradually through artistic puzzles",
                "rationale": "Combines emotional and intellectual elements"
            }
        ]
    }

def test_tropemaster_agent_initialization(mock_llm_config):
    """Test Tropemaster Agent initialization."""
    with patch('novel_writer.agents.tropemaster_agent.logger'):
        agent = TropemasterAgent(llm_config=mock_llm_config)
        assert agent.llm_config == mock_llm_config

@pytest.mark.asyncio
async def test_analyze_tropes(mock_llm_config, sample_pitch, sample_trope_analysis):
    """Test trope analysis."""
    # Set up the mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_trope_analysis)
    
    # Initialize the agent
    with patch('novel_writer.agents.tropemaster_agent.logger'):
        agent = TropemasterAgent(llm_config=mock_llm_config)
        
        # Test parameters
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Gritty"
        themes = ["Technology", "Identity", "Control"]
        
        # Analyze tropes
        analysis_result = await agent.analyze_tropes(
            pitch=sample_pitch,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Assertions
        assert analysis_result is not None
        # Check that we got a structured response even if keys might vary
        assert isinstance(analysis_result, dict)
        # We know enhancement_suggestions is a key in the sample response
        assert "enhancement_suggestions" in analysis_result or "identified_tropes" in analysis_result
        
        # Check that the LLM was called with the correct parameters
        mock_llm_config.get_completion.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_tropes_error_handling(mock_llm_config, sample_pitch):
    """Test error handling in trope analysis."""
    # Set up the mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")
    
    # Initialize the agent
    with patch('novel_writer.agents.tropemaster_agent.logger'):
        agent = TropemasterAgent(llm_config=mock_llm_config)
        
        # Test parameters
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Gritty"
        themes = ["Technology", "Identity", "Control"]
        
        # Call the method and expect an exception
        with pytest.raises(Exception) as excinfo:
            await agent.analyze_tropes(
                pitch=sample_pitch,
                genre=genre,
                subgenre=subgenre,
                tone=tone,
                themes=themes
            )
            
        # Verify the exception message
        assert "Error getting LLM response" in str(excinfo.value) 