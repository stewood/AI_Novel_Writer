"""Genre and Vibe Generator Agent for novel idea generation."""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from novelwriter_idea.config.llm import LLMConfig

logger = logging.getLogger(__name__)

class GenreVibeAgent:
    """Agent responsible for genre selection and tone/themes generation."""

    def __init__(self, llm_config: LLMConfig, data_path: Optional[Path] = None):
        """Initialize the Genre and Vibe Generator Agent.
        
        Args:
            llm_config: Configuration for the LLM client
            data_path: Optional path to the data directory. If None, uses default.
        """
        logger.debug("Initializing Genre and Vibe Generator Agent")
        self.llm_config = llm_config
        self.data_path = data_path
        logger.superdebug(f"Using data path: {self.data_path}")
        self.subgenres = self._load_subgenres()
        logger.debug(f"Loaded {sum(len(v) for v in self.subgenres.values())} subgenres across {len(self.subgenres)} main genres")

    def _load_subgenres(self) -> Dict[str, List[str]]:
        """Load subgenres from the data file.
        
        Returns:
            Dictionary mapping main genres to lists of subgenres
        """
        if self.data_path:
            data_file = self.data_path / "subgenres.json"
        else:
            data_file = Path(__file__).parent.parent / "data" / "subgenres.json"
        
        logger.debug(f"Loading subgenres from {data_file}")
        try:
            with open(data_file, "r") as f:
                data = json.load(f)
                logger.superdebug(f"Loaded subgenres data: {json.dumps(data, indent=2)}")
                return data
        except FileNotFoundError:
            logger.error(f"Subgenres file not found at {data_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in subgenres file: {e}")
            raise

    def select_genre(self, genre: Optional[str] = None) -> Tuple[str, str]:
        """Select a genre and subgenre.
        
        Args:
            genre: Optional specific genre to use. If None, randomly selects one.
            
        Returns:
            Tuple of (main_genre, subgenre)
        """
        logger.debug(f"Selecting genre (input: {genre})")
        
        if genre:
            logger.debug(f"Attempting to find specified genre: {genre}")
            # If genre is specified, find it in our subgenres
            for main_genre, subgenres in self.subgenres.items():
                logger.superdebug(f"Checking {main_genre} category for {genre}")
                if genre.lower() in [s.lower() for s in subgenres]:
                    logger.info(f"Using specified genre: {genre} (category: {main_genre})")
                    return main_genre, genre
            logger.warning(f"Specified genre '{genre}' not found, falling back to random selection")
        
        # Random selection
        main_genre = random.choice(list(self.subgenres.keys()))
        logger.debug(f"Selected main genre: {main_genre}")
        
        subgenre = random.choice(self.subgenres[main_genre])
        logger.info(f"Selected random genre: {subgenre} ({main_genre})")
        logger.superdebug(f"Available subgenres were: {self.subgenres[main_genre]}")
        
        return main_genre, subgenre

    def generate_tone_and_themes(self, genre: str, subgenre: str) -> Tuple[str, List[str]]:
        """Generate tone and themes for the story.
        
        Args:
            genre: Main genre (e.g., "science_fiction")
            subgenre: Specific subgenre (e.g., "cyberpunk")
            
        Returns:
            Tuple of (tone, themes)
        """
        logger.debug(f"Generating tone and themes for {subgenre} ({genre})")
        
        prompt = f"""Generate a tone and themes for a {subgenre} story in the {genre} genre.
        The tone should be a single word or short phrase describing the emotional/narrative style.
        The themes should be 2-5 core ideas or concepts that the story explores.
        
        Format your response as JSON:
        {{
            "tone": "the tone here",
            "themes": ["theme 1", "theme 2", "theme 3"]
        }}
        """
        
        logger.superdebug(f"Sending prompt to LLM: {prompt}")
        
        try:
            response = self.llm_config.get_completion(prompt)
            logger.superdebug(f"Received LLM response: {response}")
            
            result = json.loads(response)
            tone = result["tone"]
            themes = result["themes"]
            
            logger.info(f"Generated tone: {tone}")
            logger.info(f"Generated themes: {', '.join(themes)}")
            logger.debug(f"Full generation result: {json.dumps(result, indent=2)}")
            
            return tone, themes
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response was: {response}")
            raise ValueError("Failed to generate tone and themes: invalid JSON response") from e
        except KeyError as e:
            logger.error(f"Missing required field in LLM response: {e}")
            logger.debug(f"Response content was: {response}")
            raise ValueError("Failed to generate tone and themes: missing required field") from e 