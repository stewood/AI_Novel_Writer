"""Tests for the Meeting Recorder Agent."""

import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from novel_writer.agents.meeting_recorder_agent import MeetingRecorderAgent
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
    """Create a sample trope analysis."""
    return {
        "identified_tropes": [
            {
                "trope": "AI Control of Society",
                "description": "AI systems controlling a major aspect of human life (creativity)",
                "common_usage": "Usually portrayed as purely dystopian control",
                "current_handling": "More nuanced approach with AI potentially enhancing human creativity",
                "originality_score": 8
            }
        ],
        "subversion_suggestions": [
            {
                "trope": "AI Control of Society",
                "suggestion": "Explore AI as a collaborative partner rather than controller",
                "impact": "Creates a more nuanced exploration of human-AI relationships"
            }
        ],
        "original_elements": [
            "AI as a potential amplifier of human creativity",
            "Hidden network of human artists working with AI"
        ],
        "enhancement_suggestions": [
            {
                "element": "Hidden artist network",
                "suggestion": "Show various approaches to human-AI collaboration",
                "rationale": "Demonstrates the complexity of the central theme"
            }
        ]
    }

def test_meeting_recorder_agent_initialization(mock_llm_config, mock_logger):
    """Test Meeting Recorder Agent initialization."""
    agent = MeetingRecorderAgent(llm_config=mock_llm_config, logger=mock_logger)
    assert agent.llm_config == mock_llm_config
    assert agent.logger == mock_logger
    mock_logger.info.assert_called_once_with("Initializing Meeting Recorder Agent")

def test_generate_doc_id():
    """Test document ID generation."""
    agent = MeetingRecorderAgent()
    title = "Test Story Title"
    doc_id = agent._generate_doc_id(title)
    
    # Check format
    assert doc_id.startswith("idea_teststorytitle_")
    assert len(doc_id) > len("idea_teststorytitle_")
    
    # Check timestamp format
    timestamp = doc_id.split("_")[-1]
    assert len(timestamp) == 14  # YYYYMMDDhhmmss

def test_generate_frontmatter():
    """Test frontmatter generation."""
    agent = MeetingRecorderAgent()
    
    title = "Test Story"
    genre = "Science Fiction"
    tone = "Dark and Gritty"
    themes = ["Technology", "Humanity"]
    additional_tags = ["Test", "Example"]
    
    frontmatter = agent._generate_frontmatter(
        title=title,
        genre=genre,
        tone=tone,
        themes=themes,
        tags=additional_tags
    )
    
    # Check required fields
    assert frontmatter["doc_type"] == "idea"
    assert frontmatter["status"] == "winner"
    assert frontmatter["version"] == "v1"
    assert frontmatter["title"] == title
    assert frontmatter["genre"] == genre
    assert frontmatter["tone"] == tone
    assert frontmatter["themes"] == themes
    
    # Check tags
    expected_tags = [
        "science_fiction",
        "dark_and_gritty",
        "ai_generated",
        "technology",
        "humanity",
        "test",
        "example"
    ]
    assert sorted(frontmatter["tags"]) == sorted(expected_tags)

def test_format_trope_section(sample_trope_analysis):
    """Test trope section formatting."""
    agent = MeetingRecorderAgent()
    formatted = agent._format_trope_section(sample_trope_analysis)
    
    # Check section headers
    assert "## Identified Tropes" in formatted
    assert "## Trope Subversion Suggestions" in formatted
    assert "## Original Elements" in formatted
    assert "## Enhancement Suggestions" in formatted
    
    # Check content
    assert "AI Control of Society" in formatted
    assert "Usually portrayed as purely dystopian control" in formatted
    assert "AI as a potential amplifier of human creativity" in formatted
    assert "Show various approaches to human-AI collaboration" in formatted

@pytest.mark.asyncio
async def test_process_with_output_dir(mock_logger, sample_pitch, sample_trope_analysis):
    """Test document generation with specified output directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup
        output_dir = Path(temp_dir)
        agent = MeetingRecorderAgent(logger=mock_logger)
        
        # Process
        result = await agent.process(
            pitch=sample_pitch,
            genre="Science Fiction",
            tone="Thoughtful",
            themes=["AI", "Creativity"],
            trope_analysis=sample_trope_analysis,
            output_dir=output_dir
        )
        
        # Check result
        assert result["status"] == "success"
        assert Path(result["file_path"]).exists()
        
        # Read generated file
        content = Path(result["file_path"]).read_text(encoding='utf-8')
        
        # Check frontmatter
        assert content.startswith("---")
        frontmatter_end = content.find("---", 3)
        frontmatter = yaml.safe_load(content[3:frontmatter_end])
        
        assert frontmatter["title"] == sample_pitch["title"]
        assert "ai_generated" in frontmatter["tags"]
        
        # Check content sections
        assert "## Elevator Pitch" in content
        assert sample_pitch["hook"] in content
        assert "## Concept" in content
        assert sample_pitch["concept"] in content
        assert "## Core Conflict" in content
        assert sample_pitch["conflict"] in content
        assert "## Key Twist" in content
        assert sample_pitch["twist"] in content
        
        # Check trope analysis
        assert "## Identified Tropes" in content
        assert "## Trope Subversion Suggestions" in content
        assert "## Original Elements" in content
        assert "## Enhancement Suggestions" in content

@pytest.mark.asyncio
async def test_process_error_handling(mock_logger):
    """Test error handling in document generation."""
    agent = MeetingRecorderAgent(logger=mock_logger)
    
    with pytest.raises(KeyError):
        await agent.process(
            pitch={},  # Empty pitch will cause KeyError
            genre="Science Fiction",
            tone="Dark",
            themes=["Technology"],
            trope_analysis={}
        )
    
    mock_logger.error.assert_called() 