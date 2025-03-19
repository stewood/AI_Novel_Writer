import asyncio
import os
import logging
import traceback
from novelwriter_idea.agents.genre_vibe_agent import GenreVibeAgent
from novelwriter_idea.config.llm import LLMConfig

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_genre_vibe_agent():
    try:
        # Initialize LLM config
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        logger.info("Initializing LLM config")
        llm_config = LLMConfig(api_key=api_key)
        
        # Initialize agent
        logger.info("Initializing GenreVibeAgent")
        agent = GenreVibeAgent(llm_config)
        
        # Test genre selection
        logger.info("Testing genre selection...")
        genre, subgenre = agent.select_genre()
        logger.info(f"Selected genre: {genre}")
        logger.info(f"Selected subgenre: {subgenre}")
        
        # Test tone and themes generation
        logger.info("Testing tone and themes generation...")
        tone, themes = await agent.generate_tone_and_themes(genre, subgenre)
        logger.info(f"Generated tone: {tone}")
        logger.info("Generated themes:")
        for theme in themes:
            logger.info(f"- {theme}")
            
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Error during test: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(test_genre_vibe_agent()) 