import asyncio
import os
import logging
import tempfile
from pathlib import Path
from novel_writer.cli import _idea_async

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_idea_command():
    """Test the idea command end-to-end."""
    try:
        # Initialize a temporary output file
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as temp:
            output_path = Path(temp.name)
        
        # Run the idea command
        logger.info(f"Running idea command with output to {output_path}")
        
        # Specify a specific genre to make the test more predictable
        await _idea_async(
            genre="cyberpunk",  # Use a specific genre for consistency
            output=output_path
        )
        
        # Verify the output file exists and has content
        if output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"Output file exists with size: {file_size} bytes")
            
            # Read and log the first few lines to verify content
            with open(output_path, 'r') as f:
                first_lines = ''.join(f.readlines()[:10])
                logger.info(f"File begins with:\n{first_lines}")
            
            logger.info("Test completed successfully!")
        else:
            logger.error(f"Output file does not exist: {output_path}")
            raise FileNotFoundError(f"Output file not created: {output_path}")
    except Exception as e:
        logger.error(f"Error during test: {e}")
        raise
    finally:
        # Clean up
        try:
            if output_path.exists():
                output_path.unlink()
                logger.info(f"Deleted temporary file: {output_path}")
        except Exception as cleanup_error:
            logger.warning(f"Error cleaning up: {cleanup_error}")

if __name__ == "__main__":
    asyncio.run(test_idea_command()) 