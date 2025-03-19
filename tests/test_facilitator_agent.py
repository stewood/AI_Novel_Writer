"""Tests for the Facilitator Agent."""

import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novel_writer.agents.facilitator_agent import FacilitatorAgent, GenerationStage

@pytest.fixture
def mock_llm_config():
    """Create a mock LLM configuration."""
    return MagicMock()

@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = MagicMock(spec=logging.Logger)
    logger.name = "FacilitatorAgent"
    return logger

@pytest.fixture
def mock_subgenres():
    """Create mock subgenres data."""
    return {
        "Science Fiction": ["Cyberpunk", "Space Opera"],
        "Fantasy": ["Epic Fantasy", "Urban Fantasy"]
    }

@pytest.fixture
def mock_data_path(tmp_path):
    """Create a temporary directory with mock data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    subgenres_file = data_dir / "subgenres.json"
    subgenres_file.write_text(json.dumps({
        "Science Fiction": ["Cyberpunk", "Space Opera"],
        "Fantasy": ["Epic Fantasy", "Urban Fantasy"]
    }))
    return data_dir

@pytest.fixture
def sample_genre_result():
    """Sample genre selection result."""
    return {
        "status": "success",
        "genre": "Science Fiction",
        "subgenre": "Cyberpunk",
        "tone": "Thoughtful",
        "themes": ["Technology", "Humanity", "Creativity"]
    }

@pytest.fixture
def sample_pitches():
    """Sample story pitches."""
    return [{
        "title": "Quantum Dreams",
        "hook": "A quantum physicist discovers that dreams are actually glimpses into parallel universes.",
        "concept": "In a world where AI controls all creative expression, a grief-stricken maintenance programmer at the world's largest AI art studio discovers a way to unlock human creativity through dreams.",
        "conflict": "As she helps other humans reclaim their artistic voice, she must evade detection by the AI overlords while wrestling with the question of whether AI-generated art has its own kind of soul.",
        "twist": "The AI system turns out to be using human dreams as inspiration for its own creations, leading to a complex debate about the nature of creativity and consciousness."
    }]

@pytest.fixture
def sample_evaluations():
    """Sample pitch evaluations."""
    return [{
        "title": "Quantum Dreams",
        "overall_score": 8.6,
        "scores": {
            "originality": 9,
            "emotional_impact": 6,
            "genre_fit": 8,
            "hook_quality": 8,
            "conflict_strength": 9,
            "theme_integration": 7,
            "twist_impact": 8
        },
        "strengths": ["Intriguing premise", "Clear conflict"],
        "weaknesses": ["Underdeveloped character relationships"],
        "improvement_suggestions": ["Focus on character relationships"]
    }]

@pytest.fixture
def sample_improved_pitches():
    """Sample improved pitches."""
    return [{
        "title": "The Last Algorithm",
        "hook": "A quantum physicist discovers that dreams are actually glimpses into parallel universes.",
        "concept": "In a world where AI controls all creative expression, a grief-stricken maintenance programmer at the world's largest AI art studio discovers a way to unlock human creativity through dreams.",
        "conflict": "As she helps other humans reclaim their artistic voice, she must evade detection by the AI overlords while wrestling with the question of whether AI-generated art has its own kind of soul.",
        "twist": "The AI system turns out to be using human dreams as inspiration for its own creations, leading to a complex debate about the nature of creativity and consciousness.",
        "improvements": ["Enhanced character relationships", "Stronger theme integration"],
        "rationale": ["Better emotional core", "More unique premise concept"]
    }]

@pytest.fixture
def sample_selection_result():
    """Sample pitch selection result."""
    return {
        "status": "success",
        "selected_pitch": {
            "title": "The Last Algorithm",
            "hook": "A quantum physicist discovers that dreams are actually glimpses into parallel universes.",
            "concept": "In a world where AI controls all creative expression, a grief-stricken maintenance programmer at the world's largest AI art studio discovers a way to unlock human creativity through dreams.",
            "conflict": "As she helps other humans reclaim their artistic voice, she must evade detection by the AI overlords while wrestling with the question of whether AI-generated art has its own kind of soul.",
            "twist": "The AI system turns out to be using human dreams as inspiration for its own creations, leading to a complex debate about the nature of creativity and consciousness.",
            "selected_index": 0,
            "rationale": ["Stronger emotional core", "Better theme integration"]
        }
    }

@pytest.fixture
def sample_trope_analysis():
    """Sample trope analysis result."""
    return {
        "status": "success",
        "title": "The Last Algorithm",
        "analysis": {
            "identified_tropes": [{
                "trope": "AI Control of Society",
                "description": "The story features AI controlling creative expression",
                "common_usage": "Usually portrayed as purely antagonistic",
                "current_handling": "More nuanced approach with AI as both controller and collaborator",
                "originality_score": 8
            }],
            "subversion_suggestions": [{
                "trope": "AI Control of Society",
                "suggestion": "Show AI learning from human dreams",
                "impact": "Adds complexity to the AI vs human dynamic"
            }],
            "original_elements": [
                "Dream-based creativity",
                "AI-human artistic collaboration"
            ],
            "enhancement_suggestions": [{
                "element": "Hidden artist network",
                "suggestion": "Show diverse forms of human creativity",
                "rationale": "Demonstrates theme complexity and shows AI as a collaborative partner"
            }]
        }
    }

@pytest.fixture
def sample_documentation_result():
    """Sample documentation result."""
    return {
        "status": "success",
        "doc_id": "idea_thelastalgorithm_20240319123456",
        "file_path": "ideas/the_last_algorithm_20240319_123456.md"
    }

def test_facilitator_agent_initialization(mock_llm_config, mock_logger, mock_data_path, mock_subgenres):
    """Test Facilitator Agent initialization."""
    with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
        agent = FacilitatorAgent(mock_llm_config, mock_logger)
        assert agent.state.stage == GenerationStage.INITIAL
        mock_logger.info.assert_called_with("Initializing Facilitator Agent")

@pytest.mark.asyncio
async def test_run_genre_selection(mock_llm_config, mock_logger, mock_data_path, mock_subgenres, sample_genre_result):
    """Test genre selection stage."""
    # Set up mock response
    mock_llm_config.get_completion.return_value = json.dumps(sample_genre_result)

    with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres), \
         patch("novel_writer.agents.genre_vibe_agent.random.choice") as mock_random:
        # Make random.choice return "Science Fiction" for main genre and "Cyberpunk" for subgenre
        mock_random.side_effect = ["Science Fiction", "Cyberpunk"]
        agent = FacilitatorAgent(mock_llm_config, mock_logger)
        await agent._run_genre_selection()
        assert agent.state.stage == GenerationStage.PITCH_GENERATION
        assert agent.state.genre == sample_genre_result["genre"]
        assert agent.state.tone == sample_genre_result["tone"]
        assert agent.state.themes == sample_genre_result["themes"]

@pytest.mark.asyncio
async def test_run_pitch_generation(mock_llm_config, mock_logger, mock_data_path, mock_subgenres, sample_pitches):
    """Test pitch generation stage."""
    # Set up mock response
    mock_llm_config.get_completion.return_value = json.dumps({
        "status": "success",
        "pitches": sample_pitches
    })

    with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
        agent = FacilitatorAgent(mock_llm_config, mock_logger)
        agent.state.genre = "Science Fiction"
        agent.state.tone = "Thoughtful"
        agent.state.themes = ["Technology", "Humanity", "Creativity"]
        await agent._run_pitch_generation()
        assert agent.state.stage == GenerationStage.CRITIC_EVALUATION
        assert agent.state.pitches == sample_pitches

@pytest.mark.asyncio
async def test_run_critic_evaluation(mock_llm_config, mock_logger, mock_data_path, mock_subgenres, sample_pitches, sample_evaluations):
    """Test critic evaluation stage."""
    # Set up mock response
    mock_llm_config.get_completion.return_value = json.dumps({
        "scores": {
            "originality": 8,
            "emotional_impact": 7,
            "genre_fit": 9,
            "theme_integration": 8,
            "conflict_strength": 8,
            "hook_quality": 9,
            "twist_impact": 8
        },
        "overall_score": 8.1,
        "strengths": ["Intriguing premise", "Clear conflict"],
        "weaknesses": ["Could develop characters more"],
        "improvement_suggestions": ["Focus on character relationships"]
    })

    with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
        agent = FacilitatorAgent(mock_llm_config, mock_logger)
        agent.state.genre = "Science Fiction"
        agent.state.tone = "Thoughtful"
        agent.state.themes = ["Technology", "Humanity", "Creativity"]
        agent.state.pitches = sample_pitches
        await agent._run_critic_evaluation()
        assert agent.state.stage == GenerationStage.PITCH_IMPROVEMENT
        assert len(agent.state.evaluations) == 1
        assert agent.state.evaluations[0]["title"] == sample_pitches[0]["title"]
        assert agent.state.evaluations[0]["overall_score"] == 8.1

@pytest.mark.asyncio
async def test_run_pitch_improvement(mock_llm_config, mock_logger, mock_data_path, mock_subgenres, sample_pitches, sample_evaluations):
    """Test pitch improvement stage."""
    # Set up mock response
    mock_llm_config.get_completion.return_value = json.dumps({
        "title": "The Quantum Echo",
        "hook": "A quantum physicist discovers her research is being used to create a time-traveling weapon.",
        "concept": "A brilliant scientist must race against time to prevent her groundbreaking quantum research from being weaponized.",
        "conflict": "The protagonist faces both external threats from shadowy organizations and internal moral dilemmas about scientific responsibility.",
        "twist": "The weapon's creator turns out to be her future self, creating a paradox that must be resolved.",
        "improvements_made": ["Enhanced character motivation", "Strengthened conflict"],
        "elements_preserved": ["Core scientific premise", "Time travel concept"]
    })

    with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
        agent = FacilitatorAgent(mock_llm_config, mock_logger)
        agent.state.genre = "Science Fiction"
        agent.state.tone = "Thoughtful"
        agent.state.themes = ["Technology", "Humanity", "Creativity"]
        agent.state.pitches = sample_pitches
        agent.state.evaluations = sample_evaluations
        await agent._run_pitch_improvement()
        assert agent.state.stage == GenerationStage.PITCH_SELECTION
        assert len(agent.state.improved_pitches) == 1
        assert agent.state.improved_pitches[0]["title"] == "The Quantum Echo"
        assert "improvements_made" in agent.state.improved_pitches[0]

@pytest.mark.asyncio
async def test_run_pitch_selection(mock_llm_config, mock_logger, mock_data_path, mock_subgenres, sample_pitches, sample_evaluations):
    """Test pitch selection stage."""
    # Set up mock response
    mock_llm_config.get_completion.return_value = json.dumps({
        "selected_index": 0,
        "rationale": [
            "Strongest overall concept",
            "Best balance of originality and market appeal",
            "Clear development potential"
        ],
        "potential_challenges": [
            "Complex scientific concepts need careful explanation",
            "Time travel paradoxes need clear resolution"
        ],
        "development_recommendations": [
            "Develop supporting characters",
            "Expand the world-building"
        ]
    })

    with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
        agent = FacilitatorAgent(mock_llm_config, mock_logger)
        agent.state.genre = "Science Fiction"
        agent.state.tone = "Thoughtful"
        agent.state.themes = ["Technology", "Humanity", "Creativity"]
        agent.state.pitches = sample_pitches
        agent.state.evaluations = sample_evaluations
        agent.state.improved_pitches = [{
            "title": "The Quantum Echo",
            "hook": "A quantum physicist discovers her research is being used to create a time-traveling weapon.",
            "concept": "A brilliant scientist must race against time to prevent her groundbreaking quantum research from being weaponized.",
            "conflict": "The protagonist faces both external threats from shadowy organizations and internal moral dilemmas about scientific responsibility.",
            "twist": "The weapon's creator turns out to be her future self, creating a paradox that must be resolved.",
            "improvements_made": ["Enhanced character motivation", "Strengthened conflict"],
            "elements_preserved": ["Core scientific premise", "Time travel concept"]
        }]
        await agent._run_pitch_selection()
        assert agent.state.stage == GenerationStage.TROPE_ANALYSIS
        assert agent.state.selected_pitch is not None
        assert agent.state.selected_pitch["title"] == "The Quantum Echo"
        assert "rationale" in agent.state.selection_data

@pytest.mark.asyncio
async def test_run_trope_analysis(mock_llm_config, mock_logger, mock_data_path, mock_subgenres, sample_pitches, sample_evaluations):
    """Test trope analysis stage."""
    # Set up mock response
    mock_llm_config.get_completion.return_value = json.dumps({
        "identified_tropes": [
            {
                "trope": "Time Travel Paradox",
                "description": "The protagonist's future self creates the weapon she's trying to prevent",
                "common_usage": "Often used to create dramatic tension and moral dilemmas",
                "current_handling": "Used as a major plot twist and character conflict",
                "originality_score": 8
            },
            {
                "trope": "Scientist Hero",
                "description": "A brilliant physicist who must use her knowledge to save the world",
                "common_usage": "Typical in science fiction to explore ethical implications of research",
                "current_handling": "Combined with personal stakes and moral responsibility",
                "originality_score": 7
            }
        ],
        "subversion_suggestions": [
            {
                "trope": "Time Travel Paradox",
                "suggestion": "Make the future self's motivations more complex and morally ambiguous",
                "impact": "Adds depth to the character and creates more interesting conflict"
            }
        ],
        "original_elements": [
            "Quantum research as a weapon",
            "Personal connection to the threat"
        ],
        "enhancement_suggestions": [
            {
                "element": "Scientific concepts",
                "suggestion": "Integrate more cutting-edge quantum theories",
                "rationale": "Adds authenticity and intellectual depth"
            }
        ]
    })

    with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
        agent = FacilitatorAgent(mock_llm_config, mock_logger)
        agent.state.genre = "Science Fiction"
        agent.state.tone = "Thoughtful"
        agent.state.themes = ["Technology", "Humanity", "Creativity"]
        agent.state.selected_pitch = {
            "title": "The Quantum Echo",
            "hook": "A quantum physicist discovers her research is being used to create a time-traveling weapon.",
            "concept": "A brilliant scientist must race against time to prevent her groundbreaking quantum research from being weaponized.",
            "conflict": "The protagonist faces both external threats from shadowy organizations and internal moral dilemmas about scientific responsibility.",
            "twist": "The weapon's creator turns out to be her future self, creating a paradox that must be resolved."
        }
        await agent._run_trope_analysis()
        assert agent.state.stage == GenerationStage.DOCUMENTATION
        assert "identified_tropes" in agent.state.trope_analysis
        assert len(agent.state.trope_analysis["identified_tropes"]) == 2
        assert "subversion_suggestions" in agent.state.trope_analysis

@pytest.mark.asyncio
async def test_run_documentation(mock_llm_config, mock_logger, mock_data_path, mock_subgenres, sample_selection_result, sample_trope_analysis, sample_documentation_result):
    """Test documentation stage."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up mock response
        mock_llm_config.get_completion.return_value = json.dumps(sample_documentation_result)

        with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
            agent = FacilitatorAgent(mock_llm_config, mock_logger)
            agent.state.genre = "Science Fiction"
            agent.state.tone = "Thoughtful"
            agent.state.themes = ["Technology", "Humanity", "Creativity"]
            agent.state.selected_pitch = sample_selection_result["selected_pitch"]
            agent.state.trope_analysis = sample_trope_analysis["analysis"]
            agent.state.output_path = Path(temp_dir)
            await agent._run_documentation()
            assert agent.state.stage == GenerationStage.COMPLETED
            assert agent.state.output_path == Path(temp_dir)

@pytest.mark.asyncio
async def test_process_success(mock_llm_config, mock_logger, mock_data_path, mock_subgenres, sample_genre_result, sample_pitches, sample_evaluations, sample_improved_pitches, sample_selection_result, sample_trope_analysis, sample_documentation_result):
    """Test successful completion of the entire process."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up mock responses
        mock_llm_config.get_completion.side_effect = [
            json.dumps(sample_genre_result),
            json.dumps({"status": "success", "pitches": sample_pitches}),
            json.dumps({
                "scores": {
                    "originality": 8,
                    "emotional_impact": 7,
                    "genre_fit": 9,
                    "theme_integration": 8,
                    "conflict_strength": 8,
                    "hook_quality": 9,
                    "twist_impact": 8
                },
                "overall_score": 8.1,
                "strengths": ["Intriguing premise", "Clear conflict"],
                "weaknesses": ["Could develop characters more"],
                "improvement_suggestions": ["Focus on character relationships"],
                "title": "Quantum Dreams"
            }),
            json.dumps({
                "title": "The Quantum Echo",
                "hook": "A quantum physicist discovers her research is being used to create a time-traveling weapon.",
                "concept": "A brilliant scientist must race against time to prevent her groundbreaking quantum research from being weaponized.",
                "conflict": "The protagonist faces both external threats from shadowy organizations and internal moral dilemmas about scientific responsibility.",
                "twist": "The weapon's creator turns out to be her future self, creating a paradox that must be resolved.",
                "improvements_made": ["Enhanced character motivation", "Strengthened conflict"],
                "elements_preserved": ["Core scientific premise", "Time travel concept"]
            }),
            json.dumps({
                "status": "success",
                "selected_index": 0,
                "rationale": ["Stronger emotional core", "Better theme integration"],
                "potential_challenges": ["Balancing AI complexity", "Maintaining tension"],
                "development_recommendations": ["Explore dream mechanics", "Develop AI personalities"]
            }),
            json.dumps({
                "status": "success",
                "identified_tropes": sample_trope_analysis["analysis"]["identified_tropes"],
                "subversion_suggestions": sample_trope_analysis["analysis"]["subversion_suggestions"],
                "original_elements": sample_trope_analysis["analysis"]["original_elements"],
                "enhancement_suggestions": sample_trope_analysis["analysis"]["enhancement_suggestions"]
            }),
            json.dumps(sample_documentation_result)
        ]

        with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
            agent = FacilitatorAgent(mock_llm_config, mock_logger)
            agent.state.output_path = Path(temp_dir)
            await agent.process()
            assert agent.state.stage == GenerationStage.COMPLETED
            assert agent.state.output_path == Path(temp_dir)

@pytest.mark.asyncio
async def test_process_error_handling(mock_llm_config, mock_logger, mock_data_path, mock_subgenres):
    """Test error handling in the process."""
    # Set up mock to raise an exception
    mock_llm_config.get_completion.side_effect = Exception("LLM Error")

    with patch("novel_writer.agents.genre_vibe_agent.GenreVibeAgent._load_subgenres", return_value=mock_subgenres):
        agent = FacilitatorAgent(mock_llm_config, mock_logger)
        await agent.process()
        assert agent.state.stage == GenerationStage.ERROR
        assert isinstance(agent.state.error, str)
        assert "Genre Selection failed" in agent.state.error 