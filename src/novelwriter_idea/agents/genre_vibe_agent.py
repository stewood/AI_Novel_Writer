"""Genre and Vibe Generator Agent for novel idea generation."""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

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

    async def generate_tone_and_themes(self, genre: str, subgenre: str) -> Tuple[str, List[str]]:
        """Generate tone and themes for the story.
        
        Args:
            genre: Main genre category
            subgenre: Specific subgenre
            
        Returns:
            Tuple of (tone, list_of_themes)
        """
        prompt = f"""Generate a tone and themes for a {subgenre} story in the {genre} genre.

The tone should be a clear emotional/narrative style that fits the genre.
The themes should be 2-5 core ideas that will drive the story.

Return your response in this format:

# Tone and Themes

## Tone
[Your tone description here]

## Themes
- [Theme 1]
- [Theme 2]
- [Theme 3]
- [Theme 4]
- [Theme 5]

Make sure each theme is a clear, concise statement of a core idea or conflict.
"""

        response = await self._get_llm_response(prompt)
        
        # Parse the markdown response
        tone = ""
        themes = []
        
        current_section = None
        capturing_tone = False
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('## Tone'):
                current_section = 'tone'
                capturing_tone = True
            elif line.startswith('## Themes'):
                current_section = 'themes'
                capturing_tone = False
            elif line.startswith('#'):
                current_section = None
                capturing_tone = False
            elif current_section == 'tone' and capturing_tone:
                if tone:
                    tone += " " + line
                else:
                    tone = line
            elif current_section == 'themes' and line.startswith('-'):
                theme = line[1:].strip()
                if theme:
                    themes.append(theme)
        
        if not tone or not themes:
            logger.error(f"Failed to parse tone and themes from response: {response}")
            raise ValueError("Failed to parse tone and themes from response")
            
        logger.info(f"Generated tone: {tone}")
        logger.debug(f"Generated themes: {themes}")
        
        return tone, themes

    async def process(self, genre: Optional[str] = None) -> Dict:
        """Process genre selection and tone/themes generation.
        
        Args:
            genre: Optional specific genre to use. If None, randomly selects one.
            
        Returns:
            Dict containing the selected genre, tone, and themes
        """
        try:
            # Select genre
            main_genre, subgenre = self.select_genre(genre)
            
            # Generate tone and themes
            tone, themes = await self.generate_tone_and_themes(main_genre, subgenre)
            
            return {
                "status": "success",
                "genre": main_genre,
                "subgenre": subgenre,
                "tone": tone,
                "themes": themes
            }
            
        except Exception as e:
            logger.error(f"Error in genre and vibe generation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _get_llm_response(self, prompt: str) -> str:
        """Get a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response as a string
        """
        logger.debug(f"Sending prompt to LLM: {prompt}")
        
        try:
            response = await self.llm_config.get_completion(prompt)
            logger.superdebug(f"Raw LLM response: {response}")
            
            # Clean up the response
            cleaned = response.strip()
            if cleaned.startswith("```") and cleaned.endswith("```"):
                cleaned = cleaned[3:-3].strip()
            if cleaned.startswith("markdown"):
                cleaned = cleaned[8:].strip()
                
            logger.debug(f"Cleaned LLM response: {cleaned}")
            return cleaned
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            raise 