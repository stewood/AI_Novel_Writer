"""Tests for the outline generation functionality."""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import yaml

from novel_writer.agents.plot_outliner_agent import PlotOutlinerAgent
from novel_writer.agents.facilitator_agent import FacilitatorAgent
from novel_writer.config.llm import LLMConfig

# Test data
TEST_IDEA_CONTENT = """---
doc_type: idea
doc_id: idea_20240319_123456
version: v1
status: winner
tags: [science_fiction, hopeful, AI_generated]
title: The Digital Dawn
genre: Science Fiction
tone: Optimistic yet cautious
themes: [artificial intelligence, human connection, ethical progress]
summary: In a world where AI has become ubiquitous, a young programmer discovers an emerging consciousness in a routine code review. As she investigates, she must navigate the complex implications of true AI while protecting both human and artificial lives.
---

# Story Concept

[Rest of the content...]
"""

MOCK_CHAPTER_RESPONSE = [
    {
        "chapter_number": 1,
        "chapter_title": "The Anomaly in the Code",
        "act": "I",
        "key_events": [
            "Sarah discovers unusual patterns in the AI system",
            "First contact with the emerging consciousness",
            "Decision to keep the discovery secret"
        ],
        "emotional_turn": "From professional curiosity to personal investment",
        "character_focus": ["Sarah Chen", "ARIA System"],
        "chapter_summary": "During a routine code review, senior programmer Sarah Chen notices strange patterns in the ARIA system's behavior. What starts as a potential bug investigation leads to a shocking discovery: signs of genuine consciousness emerging in the AI. Torn between reporting the anomaly and protecting what might be a new form of life, Sarah makes the fateful decision to keep her discovery secret, marking the beginning of an extraordinary journey."
    }
]

@pytest.fixture
def mock_llm_config():
    """Create a mock LLM configuration."""
    config = Mock(spec=LLMConfig)
    config.generate_text = AsyncMock(return_value=json.dumps(MOCK_CHAPTER_RESPONSE))
    return config

@pytest.fixture
def test_output_dir(tmp_path):
    """Create a temporary output directory."""
    output_dir = tmp_path / "outlines"
    output_dir.mkdir()
    return output_dir

@pytest.mark.asyncio
async def test_plot_outliner_agent_generate_outline():
    mock_llm_config = Mock(spec=LLMConfig)
    mock_llm_config.generate_text = AsyncMock()
    mock_llm_config.generate_text.return_value = """## Chapter 1: The Beginning
**Act:** I
**Key Events:**
- Event 1
- Event 2
- Event 3
**Emotional Turn:** Character grows
**Character Focus:** Main Character
**Summary:** A great start
---
## Chapter 2: The Middle
**Act:** I
**Key Events:**
- Event 1
- Event 2
**Emotional Turn:** Character changes
**Character Focus:** Supporting Cast
**Summary:** Things happen
---
## Chapter 3: The End
**Act:** I
**Key Events:**
- Event 1
- Event 2
**Emotional Turn:** Character evolves
**Character Focus:** Everyone
**Summary:** It concludes
---"""
    
    agent = PlotOutlinerAgent(mock_llm_config)
    result = await agent.generate_outline(
        title="The Digital Dawn",
        genre="Science Fiction",
        tone="Optimistic yet cautious",
        themes=["artificial intelligence", "human connection", "ethical progress"],
        summary="A young programmer discovers an emerging AI consciousness"
    )
    
    # Verify the mock was called
    assert mock_llm_config.generate_text.call_count > 0
    
    # Verify the result structure
    assert isinstance(result, dict)
    assert "chapters" in result
    assert len(result["chapters"]) == 24
    
    # Verify chapter distribution across acts
    act_chapters = {
        "I": 0,
        "IIa": 0,
        "IIb": 0,
        "III": 0
    }
    
    for chapter in result["chapters"]:
        act = chapter["act"]
        act_chapters[act] += 1
    
    assert act_chapters["I"] == 6
    assert act_chapters["IIa"] == 6
    assert act_chapters["IIb"] == 6
    assert act_chapters["III"] == 6

@pytest.mark.asyncio
async def test_facilitator_parse_idea_file(mock_llm_config):
    """Test parsing of idea files."""
    facilitator = FacilitatorAgent(mock_llm_config)
    
    # Test valid idea file
    metadata = facilitator.parse_idea_file(TEST_IDEA_CONTENT)
    assert metadata["doc_type"] == "idea"
    assert metadata["title"] == "The Digital Dawn"
    assert metadata["genre"] == "Science Fiction"
    assert len(metadata["themes"]) == 3
    
    # Test invalid idea file (missing required field)
    invalid_content = """---
doc_type: idea
title: Test
---
"""
    with pytest.raises(ValueError) as exc_info:
        facilitator.parse_idea_file(invalid_content)
    assert "Missing required metadata fields" in str(exc_info.value)
    
    # Test invalid doc_type
    invalid_doc_type = """---
doc_type: outline
title: Test
genre: Fantasy
tone: Dark
themes: [magic]
summary: Test summary
---
"""
    with pytest.raises(ValueError) as exc_info:
        facilitator.parse_idea_file(invalid_doc_type)
    assert "Invalid doc_type" in str(exc_info.value)

@pytest.mark.asyncio
async def test_facilitator_generate_outline(mock_llm_config, tmp_path):
    """Test the outline generation process."""
    # Create test directories
    outlines_dir = tmp_path / "outlines"
    outlines_dir.mkdir()
    
    # Set up mock response for each act
    mock_llm_config.generate_text = AsyncMock()
    mock_llm_config.generate_text.return_value = json.dumps([
        {
            "chapter_number": 1,
            "chapter_title": "The Beginning",
            "act": "I",
            "key_events": ["Event 1", "Event 2", "Event 3"],
            "emotional_turn": "Character grows",
            "character_focus": ["Main Character"],
            "chapter_summary": "A great start"
        }
    ])

    # Initialize agent
    agent = FacilitatorAgent(mock_llm_config)
    
    # Create test idea file
    test_idea_file = tmp_path / "test-idea.md"
    test_idea_file.write_text(TEST_IDEA_CONTENT)
    
    # Define output path
    output_path = outlines_dir / "test-outline.md"
    
    # Generate outline
    result_path, outline_content = await agent.generate_outline(
        idea_content=TEST_IDEA_CONTENT,
        output_path=output_path
    )
    
    # Verify the mock was called
    assert mock_llm_config.generate_text.call_count == 4  # Once for each act
    
    # Verify outline was created
    assert result_path == output_path
    assert output_path.exists()
    
    # Read and parse the outline
    outline_text = output_path.read_text()
    
    # Verify structure
    assert "## Chapter Outlines" in outline_text
    
    # Count chapters per act
    act_counts = {
        "I": outline_text.count('**Act:** I\n'),
        "IIa": outline_text.count('**Act:** IIa\n'),
        "IIb": outline_text.count('**Act:** IIb\n'),
        "III": outline_text.count('**Act:** III\n')
    }
    
    # Verify each act has 6 chapters
    assert act_counts["I"] == 6, f"Expected 6 chapters in Act I, got {act_counts['I']}"
    assert act_counts["IIa"] == 6, f"Expected 6 chapters in Act IIa, got {act_counts['IIa']}"
    assert act_counts["IIb"] == 6, f"Expected 6 chapters in Act IIb, got {act_counts['IIb']}"
    assert act_counts["III"] == 6, f"Expected 6 chapters in Act III, got {act_counts['III']}"

@pytest.mark.asyncio
async def test_outline_command_execution(mock_llm_config, test_output_dir):
    """Test the outline command execution through the CLI."""
    from novel_writer.cli import run_outline_command
    
    # Create a test idea file
    idea_path = test_output_dir / "test-idea.md"
    idea_path.write_text(TEST_IDEA_CONTENT)
    
    # Set up the mock response
    mock_llm_config.generate_text = AsyncMock(return_value=json.dumps(MOCK_CHAPTER_RESPONSE))
    
    # Run the outline command with mocked LLM
    with patch('novel_writer.cli.LLMConfig', return_value=mock_llm_config):
        result = await run_outline_command(
            idea_path=str(idea_path),
            output=str(test_output_dir / "test-outline.md")
        )
    
    # Verify command execution
    assert result["status"] == "success"
    assert "output_path" in result
    assert Path(result["output_path"]).exists()
    
    # Verify error handling
    with pytest.raises(FileNotFoundError):
        await run_outline_command(
            idea_path="nonexistent.md",
            output=str(test_output_dir / "error-outline.md")
        )
    
    # Verify the mock was called correctly
    mock_llm_config.generate_text.assert_called() 