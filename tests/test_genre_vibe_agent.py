"""Tests for the Genre and Vibe Generator Agent."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from novel_writer.agents.genre_vibe_agent import GenreVibeAgent
from novel_writer.config.llm import LLMConfig

@pytest.fixture
def mock_llm_config():
    """Create a mock LLM configuration."""
    return MagicMock(spec=LLMConfig)

@pytest.fixture
def sample_subgenres(tmp_path):
    """Create a temporary subgenres.json file."""
    data = {
        "science_fiction": ["cyberpunk", "space opera"],
        "fantasy": ["grimdark", "high fantasy"]
    }
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    with open(data_dir / "subgenres.json", "w") as f:
        json.dump(data, f)
    return data_dir

def test_genre_vibe_agent_initialization(mock_llm_config, sample_subgenres):
    """Test GenreVibeAgent initialization."""
    agent = GenreVibeAgent(mock_llm_config, data_path=sample_subgenres)
    assert agent.llm_config == mock_llm_config
    assert "science_fiction" in agent.subgenres
    assert "fantasy" in agent.subgenres

def test_select_genre_random(mock_llm_config, sample_subgenres):
    """Test random genre selection."""
    agent = GenreVibeAgent(mock_llm_config, data_path=sample_subgenres)
    main_genre, subgenre = agent.select_genre()
    assert main_genre in ["science_fiction", "fantasy"]
    assert subgenre in agent.subgenres[main_genre]

def test_select_genre_specific(mock_llm_config, sample_subgenres):
    """Test specific genre selection."""
    agent = GenreVibeAgent(mock_llm_config, data_path=sample_subgenres)
    main_genre, subgenre = agent.select_genre("cyberpunk")
    assert main_genre == "science_fiction"
    assert subgenre == "cyberpunk"

def test_select_genre_invalid(mock_llm_config, sample_subgenres):
    """Test handling of invalid genre."""
    agent = GenreVibeAgent(mock_llm_config, data_path=sample_subgenres)
    main_genre, subgenre = agent.select_genre("invalid_genre")
    assert main_genre in ["science_fiction", "fantasy"]
    assert subgenre in agent.subgenres[main_genre]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_tone_and_themes(mock_llm_config, sample_subgenres):
    """Test tone and themes generation."""
    mock_response = """# Tone and Themes

## Tone
dark and gritty

## Themes
- redemption
- sacrifice
- hope
"""
    mock_llm_config.get_completion.return_value = mock_response
    
    agent = GenreVibeAgent(mock_llm_config, data_path=sample_subgenres)
    tone, themes = await agent.generate_tone_and_themes("fantasy", "grimdark")
    assert tone == "dark and gritty"
    assert themes == ["redemption", "sacrifice", "hope"] 