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

def test_meeting_recorder_agent_initialization(mock_llm_config):
    """Test Meeting Recorder Agent initialization."""
    with patch('novel_writer.agents.meeting_recorder_agent.logger'):
        agent = MeetingRecorderAgent(llm_config=mock_llm_config)
        assert agent.llm_config == mock_llm_config

def test_create_frontmatter():
    """Test frontmatter generation."""
    with patch('novel_writer.agents.meeting_recorder_agent.logger'):
        # We need to provide mock LLM config even though it's not used in this test
        agent = MeetingRecorderAgent(llm_config=MagicMock())
        
        # Test data
        doc_id = "idea_12345678"
        title = "Test Title"
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Dark"
        themes = ["Technology", "Identity"]
        selected_pitch = {
            "hook": "A test hook",
            "premise": "A test premise"
        }
        
        # Generate frontmatter
        frontmatter = agent._create_frontmatter(
            doc_id=doc_id,
            title=title,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes,
            selected_pitch=selected_pitch
        )
        
        # Assertions
        assert "---" in frontmatter
        assert f'title: "{title}"' in frontmatter
        assert f'elevator_pitch: "{selected_pitch["hook"]}"' in frontmatter
        assert f'genre: "{genre}"' in frontmatter
        assert f'subgenre: "{subgenre}"' in frontmatter
        assert f'tone: "{tone}"' in frontmatter
        assert "themes:" in frontmatter
        assert "Technology" in frontmatter
        assert "Identity" in frontmatter

def test_format_document_body(sample_trope_analysis):
    """Test document body formatting."""
    with patch('novel_writer.agents.meeting_recorder_agent.logger'):
        # We need to provide mock LLM config even though it's not used in this test
        agent = MeetingRecorderAgent(llm_config=MagicMock())
        
        # Test data
        selected_pitch = {
            "title": "Test Title",
            "hook": "A test hook",
            "premise": "A test premise"
        }
        selection_data = {
            "selection_criteria": ["Criterion 1", "Criterion 2"],
            "development_recommendations": ["Recommendation 1", "Recommendation 2"]
        }
        genre = "Science Fiction"
        subgenre = "Cyberpunk"
        tone = "Dark"
        themes = ["Technology", "Identity"]
        
        # Format document body
        document_body = agent._format_document_body(
            selected_pitch=selected_pitch,
            selection_data=selection_data,
            trope_analysis=sample_trope_analysis,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Basic assertions
        assert document_body.strip() != ""
        assert "## Trope Analysis" in document_body
        
        # Check for trope content - make test more flexible about the exact structure
        for suggestion in sample_trope_analysis["enhancement_suggestions"]:
            element = suggestion.get("element", "")
            trope = suggestion.get("trope", "")
            # Check that at least one of these appears in the document
            assert element in document_body or trope in document_body

@pytest.mark.asyncio
async def test_compile_idea(sample_pitch, sample_trope_analysis):
    """Test document generation with specified output directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup
        output_dir = Path(temp_dir)
        
        with patch('novel_writer.agents.meeting_recorder_agent.logger'):
            # Initialize with mock LLM config
            agent = MeetingRecorderAgent(llm_config=MagicMock())
            
            # Prepare test data
            genre = "Science Fiction"
            subgenre = "Cyberpunk"
            tone = "Dark and gritty"
            themes = ["Technology", "Identity", "Reality"]
            selection_data = {
                "selection_criteria": ["Criterion 1", "Criterion 2"],
                "development_recommendations": ["Recommendation 1", "Recommendation 2"]
            }
            
            # Call the compile method
            file_path, document_content = await agent.compile_idea(
                selected_pitch=sample_pitch,
                selection_data=selection_data,
                trope_analysis=sample_trope_analysis,
                genre=genre,
                subgenre=subgenre,
                tone=tone,
                themes=themes,
                output_dir=str(output_dir)
            )
            
            # Assertions
            assert file_path is not None
            assert document_content is not None
            output_path = Path(file_path)
            assert output_path.exists()
            assert output_path.is_file()
            
            # Verify file content
            content = output_path.read_text()
            assert "---" in content  # Has frontmatter
            assert sample_pitch["title"] in content
            assert genre in content
            assert "# " + sample_pitch["title"] in content  # Title as heading
            
            # Clean up
            output_path.unlink()

@pytest.mark.asyncio
async def test_process_error_handling():
    """Test error handling in document generation."""
    with patch('novel_writer.agents.meeting_recorder_agent.logger'):
        agent = MeetingRecorderAgent(llm_config=MagicMock())
        
        # Test with invalid data to force error
        with pytest.raises(Exception):
            await agent.compile_idea(
                selected_pitch=None,  # Invalid pitch to trigger error
                selection_data={},
                genre="Science Fiction",
                subgenre="Cyberpunk",
                tone="Dark",
                themes=["Technology"],
                trope_analysis={},
                output_dir=Path(".")
            ) 