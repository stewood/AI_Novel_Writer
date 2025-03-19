"""Command-line interface for novelwriter_idea."""

import logging
import os
from pathlib import Path

import click
from rich.console import Console

from novelwriter_idea.agents.genre_vibe_agent import GenreVibeAgent
from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.config.logging_config import setup_logging

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
def cli(log_level: str, log_file: str, no_console_log: bool):
    """NovelWriter Idea Generator - AI-powered novel idea generation tool."""
    # Set up logging
    setup_logging(
        log_level=log_level,
        log_file=None if log_file.lower() == "none" else log_file,
        console_output=not no_console_log
    )

@cli.command()
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
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize LLM configuration
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise click.ClickException("OPENROUTER_API_KEY environment variable not set")
        
        logger.debug("Initializing LLM configuration")
        llm_config = LLMConfig(api_key=api_key)
        
        # Initialize Genre and Vibe Generator Agent
        logger.debug("Creating Genre and Vibe Generator Agent")
        genre_vibe_agent = GenreVibeAgent(llm_config)
        
        # Select or generate genre
        main_genre, subgenre = genre_vibe_agent.select_genre(genre)
        console.print(f"[green]Selected genre:[/green] {subgenre} ({main_genre})")
        
        # Generate or use provided tone and themes
        if not tone or not themes:
            logger.debug("Generating tone and themes")
            generated_tone, generated_themes = genre_vibe_agent.generate_tone_and_themes(
                main_genre, subgenre
            )
            tone = tone or generated_tone
            themes = themes or generated_themes
        else:
            logger.debug(f"Using provided tone: {tone}")
            if themes:
                logger.debug(f"Using provided themes: {themes}")
        
        if isinstance(themes, str):
            themes = [t.strip() for t in themes.split(",")]
            logger.debug(f"Split themes string into list: {themes}")
        
        # Create output directory and file
        if not output:
            output_dir = Path("ideas") / "untitled"
            output_dir.mkdir(parents=True, exist_ok=True)
            output = output_dir / f"idea_{subgenre.lower()}.md"
            logger.debug(f"Created output directory: {output_dir}")
        
        # TODO: Generate the idea file with all the information
        console.print(f"[green]Idea will be saved to:[/green] {output}")
        logger.info(f"Idea file will be saved to: {output}")
        
    except Exception as e:
        logger.error(f"Error generating idea: {e}", exc_info=True)
        raise click.ClickException(str(e))

if __name__ == "__main__":
    cli() 