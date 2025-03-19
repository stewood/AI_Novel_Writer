"""Command-line interface for novelwriter_idea."""

import asyncio
import logging
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

import click
from rich.console import Console
from dotenv import load_dotenv

from novelwriter_idea.agents.facilitator_agent import FacilitatorAgent
from novelwriter_idea.agents.genre_vibe_agent import GenreVibeAgent
from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.config.logging_config import setup_logging
from novelwriter_idea.agents.pitch_generator_agent import PitchGeneratorAgent
from novelwriter_idea.agents.critic_agent import CriticAgent
from novelwriter_idea.agents.improver_agent import ImproverAgent
from novelwriter_idea.agents.voter_agent import VoterAgent
from novelwriter_idea.agents.tropemaster_agent import TropemasterAgent

# Load environment variables from .env file
load_dotenv()

console = Console()

@click.group()
@click.option(
    "--log-level",
    type=click.Choice(["ERROR", "WARN", "INFO", "DEBUG", "SUPERDEBUG"], case_sensitive=False),
    default="INFO",
    help="Set the logging level."
)
@click.option(
    "--log-file",
    type=click.Path(),
    default="logs/novelwriter.log",
    help="Path to log file. Use 'none' to disable file logging."
)
@click.option(
    "--no-console-log",
    is_flag=True,
    help="Disable console logging."
)
def main(log_level: str, log_file: str, no_console_log: bool):
    """NovelWriter Idea Generator - AI-powered novel idea generation tool."""
    # Set up logging
    setup_logging(
        log_level=log_level,
        log_file=None if log_file.lower() == "none" else log_file,
        console_output=not no_console_log
    )

@main.command()
@click.option(
    "--genre",
    type=str,
    help="Specific genre to use (e.g., 'cyberpunk', 'grimdark'). If not provided, randomly selects one."
)
@click.option(
    "--tone",
    type=str,
    help="Specific tone to use (e.g., 'dark', 'hopeful'). If not provided, generates one."
)
@click.option(
    "--themes",
    type=str,
    help="Comma-separated list of themes. If not provided, generates themes."
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output path for the idea file. If not provided, creates in ideas/ directory."
)
def idea(genre: str, tone: str, themes: str, output: str):
    """Generate a novel idea with specified or generated genre, tone, and themes."""
    asyncio.run(_idea_async(genre, tone, themes, output))

async def _idea_async(
    genre: Optional[str] = None,
    tone: Optional[str] = None,
    themes: Optional[List[str]] = None,
    output: Optional[Path] = None
) -> None:
    """Generate a story idea asynchronously."""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize LLM configuration
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise click.ClickException("OPENROUTER_API_KEY environment variable not set")
        
        logger.debug("Initializing LLM configuration")
        llm_config = LLMConfig(api_key=api_key)
        
        # Initialize agents
        logger.debug("Initializing agents")
        genre_vibe_agent = GenreVibeAgent(llm_config)
        pitch_generator = PitchGeneratorAgent(llm_config)
        critic = CriticAgent(llm_config)
        improver = ImproverAgent(llm_config)
        voter = VoterAgent(llm_config)
        tropemaster = TropemasterAgent(llm_config)
        
        # Select or use provided genre
        main_genre, subgenre = genre_vibe_agent.select_genre(genre)
        
        # Generate or use provided tone and themes
        if not tone or not themes:
            logger.debug("Generating tone and themes")
            generated_tone, generated_themes = await genre_vibe_agent.generate_tone_and_themes(
                main_genre, subgenre
            )
            tone = tone or generated_tone
            themes = themes or generated_themes
        
        # Generate pitches
        logger.debug("Generating pitches")
        pitches_result = await pitch_generator.generate_pitches(
            main_genre, subgenre, tone, themes
        )
        pitches = pitches_result["pitches"]
        
        # Evaluate pitches
        logger.debug("Evaluating pitches")
        evaluations_result = await critic.evaluate_pitches(
            pitches, main_genre, subgenre, tone, themes
        )
        evaluations = evaluations_result["evaluations"]
        
        # Improve low-scoring pitches
        improved_pitches = []
        for pitch, evaluation in zip(pitches, evaluations):
            if any(score < 8 for score in evaluation["scores"].values()):
                logger.debug(f"Improving pitch: {pitch['title']}")
                improvement_result = await improver.improve_pitch(
                    pitch, evaluation, main_genre, subgenre, tone, themes
                )
                improved_pitches.append(improvement_result["improved_pitch"])
        
        # Select best pitch
        logger.debug("Selecting best pitch")
        selection_result = await voter.select_best_pitch(
            pitches + improved_pitches,
            evaluations,
            main_genre,
            subgenre,
            tone,
            themes
        )
        
        # Find the winning pitch in our list of pitches
        winning_title = selection_result["winner"]
        selected_pitch = None
        for pitch in pitches + improved_pitches:
            if pitch["title"] == winning_title:
                selected_pitch = pitch
                break
        
        if not selected_pitch:
            logger.error(f"Could not find winning pitch with title: {winning_title}")
            raise ValueError(f"Could not find winning pitch with title: {winning_title}")
        
        logger.info(f"Selected pitch: {selected_pitch['title']}")
        
        # Analyze tropes
        logger.debug("Analyzing tropes")
        trope_analysis = await tropemaster.analyze_tropes(
            selected_pitch,
            main_genre,
            subgenre
        )
        
        # Generate output file
        if not output:
            # Create ideas directory if it doesn't exist
            ideas_dir = Path.cwd() / "ideas"
            ideas_dir.mkdir(exist_ok=True)
            
            # Create story directory
            story_title = selected_pitch["title"].lower().replace(" ", "-")
            story_dir = ideas_dir / story_title
            story_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output = story_dir / f"idea_{story_title}_{timestamp}.md"
        
        # Write the idea to file
        with open(output, "w") as f:
            f.write(f"""---
doc_type: idea
doc_id: idea_{datetime.now().strftime("%Y%m%d_%H%M%S")}
status: winner
version: v1
tags:
  - genre: {main_genre}
  - subgenre: {subgenre}
  - tone: {tone}
  - themes: {', '.join(themes)}
  - AI_generated
title: {selected_pitch["title"]}
---

# Story Idea: {selected_pitch["title"]}

## Elevator Pitch
{selected_pitch["hook"]}

## Genre & Tone
- **Genre**: {main_genre} ({subgenre})
- **Tone**: {tone}
- **Themes**: {', '.join(themes)}

## Summary
{selected_pitch["premise"]}

## Main Conflict
{selected_pitch["main_conflict"]}

## Unique Twist
{selected_pitch["unique_twist"]}

## Selection Criteria
{chr(10).join(f"- {criteria}" for criteria in selection_result["selection_criteria"])}

## Detected Tropes
{chr(10).join(f"- {trope}" for trope in trope_analysis["detected_tropes"])}

## Trope Suggestions
{chr(10).join(f"- {twist}" for twist in trope_analysis["suggested_twists"])}

## Development Recommendations
{chr(10).join(f"- {rec}" for rec in selection_result["development_recommendations"])}

## Potential Challenges
{chr(10).join(f"- {challenge}" for challenge in selection_result["potential_challenges"])}
""")
        
        logger.info(f"Successfully generated idea: {output}")
        print(f"Generated idea: {output}")
        
    except Exception as e:
        logger.error(f"Error generating idea: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 