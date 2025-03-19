import asyncio
import os
import logging
import traceback
from novelwriter_idea.agents.tropemaster_agent import TropemasterAgent
from novelwriter_idea.config.llm import LLMConfig

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_tropemaster_agent():
    try:
        # Initialize LLM config
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        logger.info("Initializing LLM config")
        llm_config = LLMConfig(api_key=api_key)
        
        # Initialize agent
        logger.info("Initializing TropemasterAgent")
        agent = TropemasterAgent(llm_config)
        
        # Create a sample pitch
        sample_pitch = {
            "title": "The Obsidian Bloom",
            "hook": "A stone carver, burdened by a lineage of failed ascensions, must choose between embracing the destructive path to immortality favored by his ancestors or forging a new way, even if it means ending his family's legacy forever.",
            "premise": "Old Master Lin is the last of a clan renowned for their mastery over earth energy, but also infamous for the monstrous transformations required to reach higher realms – transformations that stripped them of their empathy and ultimately, their humanity. He dedicates his life to the quiet art of stone carving, rejecting cultivation, yet a looming cataclysm and the desperate pleas of his village force him to confront his inheritance. He begins to cultivate, but seeks a path *around* the brutal requirements, studying forgotten techniques and ancient lore.",
            "main_conflict": "Lin's internal struggle against the inherent darkness within his bloodline and the external pressure to conform to the established, ruthless methods of achieving power. He must contend with rival sects who view his unorthodox approach as weakness, and the creeping influence of the 'Stone Rot,' a spiritual affliction that consumes those who delay their full ascension, turning them into mindless, earth-bound entities.",
            "unique_twist": "The 'Stone Rot' isn't a disease, but a manifestation of the earth's grief. The constant, forceful extraction of energy by generations of Lin's ancestors has wounded the land, and the Rot is its attempt to reclaim what was stolen. Lin discovering this forces him to choose between saving himself and healing the world, potentially sacrificing his own cultivation."
        }
        
        # Test trope analysis
        logger.info("Testing trope analysis...")
        trope_analysis = await agent.analyze_tropes(sample_pitch, "fantasy", "cultivation fantasy")
        
        # Log the results
        logger.info(f"Detected Tropes ({len(trope_analysis['detected_tropes'])}):")
        for trope in trope_analysis['detected_tropes']:
            logger.info(f"- {trope}")
            
        logger.info(f"\nSuggested Twists ({len(trope_analysis['suggested_twists'])}):")
        for twist in trope_analysis['suggested_twists']:
            logger.info(f"- {twist}")
            
        logger.info(f"\nOriginal Elements ({len(trope_analysis['original_elements'])}):")
        for element in trope_analysis['original_elements']:
            logger.info(f"- {element}")
            
        logger.info(f"\nEnhancement Suggestions ({len(trope_analysis['enhancement_suggestions'])}):")
        for suggestion in trope_analysis['enhancement_suggestions']:
            logger.info(f"- {suggestion}")
        
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Error during test: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(test_tropemaster_agent()) 