import asyncio
import os
import logging
import traceback
from novelwriter_idea.agents.voter_agent import VoterAgent
from novelwriter_idea.config.llm import LLMConfig

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_voter_agent():
    try:
        # Initialize LLM config
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        logger.info("Initializing LLM config")
        llm_config = LLMConfig(api_key=api_key)
        
        # Initialize agent
        logger.info("Initializing VoterAgent")
        agent = VoterAgent(llm_config)
        
        # Create sample pitches and evaluations
        pitches = [
            {
                "title": "The Obsidian Bloom",
                "hook": "A stone carver, burdened by a lineage of failed ascensions, must choose between embracing the destructive path to immortality favored by his ancestors or forging a new way, even if it means ending his family's legacy forever.",
                "premise": "Old Master Lin is the last of a clan renowned for their mastery over earth energy, but also infamous for the monstrous transformations required to reach higher realms – transformations that stripped them of their empathy and ultimately, their humanity. He dedicates his life to the quiet art of stone carving, rejecting cultivation, yet a looming cataclysm and the desperate pleas of his village force him to confront his inheritance. He begins to cultivate, but seeks a path *around* the brutal requirements, studying forgotten techniques and ancient lore.",
                "main_conflict": "Lin's internal struggle against the inherent darkness within his bloodline and the external pressure to conform to the established, ruthless methods of achieving power. He must contend with rival sects who view his unorthodox approach as weakness, and the creeping influence of the 'Stone Rot,' a spiritual affliction that consumes those who delay their full ascension, turning them into mindless, earth-bound entities.",
                "unique_twist": "The 'Stone Rot' isn't a disease, but a manifestation of the earth's grief. The constant, forceful extraction of energy by generations of Lin's ancestors has wounded the land, and the Rot is its attempt to reclaim what was stolen. Lin discovering this forces him to choose between saving himself and healing the world, potentially sacrificing his own cultivation."
            },
            {
                "title": "The Cartographer of Lost Echoes",
                "hook": "An aging cartographer, tasked with mapping the fading memories of a dying world, discovers that the land itself is actively forgetting its past, and he alone might hold the key to preventing its complete dissolution.",
                "premise": "The realm of Aethel is slowly unraveling, not through war or disaster, but through a gradual forgetting. Landscapes shift, histories blur, and even the gods themselves are becoming fragmented echoes. Ren, a meticulous cartographer from a secluded order dedicated to preserving knowledge, travels the land, painstakingly charting these changes. He believes that by mapping the 'lost echoes' – remnants of forgotten events and emotions imprinted on the land – he can somehow anchor Aethel to its past.",
                "main_conflict": "Ren's struggle against the relentless tide of oblivion and the apathy of those who have already begun to forget. He must navigate treacherous political landscapes as ambitious lords exploit the chaos, and confront the enigmatic 'Silencers,' beings who actively accelerate the forgetting, believing it to be a natural cycle. The core conflict lies in his personal grief and the realization that even his own memories are susceptible to the fading, questioning the value of preservation in the face of inevitable loss.",
                "unique_twist": "The Silencers aren't malicious; they are the remnants of a previous civilization that *chose* to forget a horrific past, believing oblivion was the only path to peace. They see Ren's efforts as a dangerous disruption, potentially unleashing the horrors they buried. Ren must decide if some histories are better left lost, even if it means accelerating Aethel's decline."
            }
        ]
        
        evaluations = [
            {
                "scores": {
                    "Originality": 7,
                    "Emotional Impact": 9,
                    "Genre Fit": 10,
                    "Theme Integration": 9,
                    "Commercial Potential": 7
                },
                "key_strengths": [
                    "The concept of the 'Stone Rot' as the land's grief is exceptionally creative and emotionally resonant.",
                    "The protagonist's internal conflict is richly layered and promises a compelling character arc.",
                    "The premise readily lends itself to exploration of the core themes."
                ],
                "areas_for_improvement": [
                    "The rival sects feel a bit generic; fleshing them out with unique motivations and cultivation styles would be beneficial.",
                    "The cataclysm that forces Lin to act could be more clearly defined to raise the stakes.",
                    "Consider exploring the historical context of the clan's previous failed ascensions in more detail."
                ]
            },
            {
                "scores": {
                    "Originality": 8,
                    "Emotional Impact": 8,
                    "Genre Fit": 9,
                    "Theme Integration": 8,
                    "Commercial Potential": 6
                },
                "key_strengths": [
                    "The world-building is exceptionally creative and evocative. The concept of 'lost echoes' is beautifully poetic.",
                    "The moral ambiguity of the Silencers adds a layer of complexity and nuance.",
                    "Ren's internal struggle with his own fading memories is a powerful emotional hook."
                ],
                "areas_for_improvement": [
                    "The cultivation aspect feels somewhat absent. Consider integrating more explicit cultivation mechanics or power systems tied to memory or mapping.",
                    "The 'Silencers' motivations could be expanded upon. What specifically was the 'horrific past' they sought to forget?",
                    "The political landscape feels underdeveloped; more detail would add conflict and tension."
                ]
            }
        ]
        
        # Test voter agent
        logger.info("Testing voter agent...")
        selection = await agent.select_best_pitch(
            pitches,
            evaluations,
            "fantasy",
            "cultivation fantasy",
            "wistful and determined",
            ["The Price of Immortality", "Breaking the Cycle of History", "The Illusion of Control", "Defining Self Through Adversity"]
        )
        
        # Log the results
        logger.info(f"Winner: {selection['winner']}")
        
        logger.info(f"\nSelection Criteria ({len(selection['selection_criteria'])}):")
        for criterion in selection['selection_criteria']:
            logger.info(f"- {criterion}")
            
        logger.info(f"\nDevelopment Recommendations ({len(selection['development_recommendations'])}):")
        for rec in selection['development_recommendations']:
            logger.info(f"- {rec}")
            
        logger.info(f"\nPotential Challenges ({len(selection['potential_challenges'])}):")
        for challenge in selection['potential_challenges']:
            logger.info(f"- {challenge}")
        
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Error during test: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(test_voter_agent()) 