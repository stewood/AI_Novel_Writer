import click
from pathlib import Path
from typing import Optional

from .config.logging import setup_logging
from .agents.facilitator import FacilitatorAgent

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
@click.option('--superdebug/--no-superdebug', default=False, help='Enable super detailed debug logging')
def main(debug: bool, superdebug: bool):
    """NovelWriter Idea Generator - A CLI tool for generating novel ideas using AI agents."""
    # Set up logging
    log_level = 5 if superdebug else 10 if debug else 20  # SUPERDEBUG=5, DEBUG=10, INFO=20
    setup_logging(log_level=log_level)

@main.command()
@click.option('--genre', help='Specify a genre (optional)')
@click.option('--tone', help='Specify the tone (optional)')
@click.option('--themes', help='Specify themes (optional)')
@click.option('--output', type=click.Path(), help='Specify output path (optional)')
async def idea(genre: Optional[str], tone: Optional[str], themes: Optional[str], output: Optional[str]):
    """Generate a new story idea using AI agents."""
    try:
        # Initialize the facilitator agent
        facilitator = FacilitatorAgent()
        
        # Prepare input data
        input_data = {
            'genre': genre,
            'tone': tone,
            'themes': themes.split(',') if themes else None,
            'output_path': Path(output) if output else None
        }
        
        # Run the idea generation process
        result = await facilitator.run(input_data)
        
        # Print the output path
        click.echo(f"Generated idea saved to: {result['output_path']}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main() 