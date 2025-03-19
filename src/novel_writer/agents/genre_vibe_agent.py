"""Genre and Vibe Generator Agent for novel idea generation.

This agent is responsible for selecting a genre/subgenre and generating
appropriate tone and themes for the story. It can either use a specified
genre or randomly select one from a curated list.
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from novel_writer.config.llm import LLMConfig
from novel_writer.agents.base_agent import BaseAgent

# Initialize logger
logger = logging.getLogger(__name__)

class GenreVibeAgent(BaseAgent):
    """Agent responsible for genre selection and tone/themes generation.
    
    This agent selects a genre (randomly or based on user input) and generates
    appropriate tone and themes that align with the selected genre. It serves as
    the foundation for the idea generation process.
    """

    def __init__(self, llm_config: LLMConfig, data_path: Optional[Path] = None):
        """Initialize the Genre and Vibe Generator Agent.
        
        Args:
            llm_config: Configuration for the LLM client
            data_path: Optional path to the data directory. If None, uses default.
        """
        super().__init__(llm_config)
        logger.info("Initializing Genre and Vibe Generator Agent")
        
        self.data_path = data_path
        logger.debug(f"Using data path: {self.data_path}")
        
        self.subgenres = self._load_subgenres()
        logger.info(f"Loaded {sum(len(v) for v in self.subgenres.values())} subgenres across {len(self.subgenres)} main genres")
        logger.superdebug(f"Full subgenres dictionary: {self.subgenres}")

    def _load_subgenres(self) -> Dict[str, List[str]]:
        """Load subgenres from the data file.
        
        Returns:
            Dictionary mapping main genres to lists of subgenres
            
        Raises:
            FileNotFoundError: If the subgenres file is not found
            JSONDecodeError: If the subgenres file contains invalid JSON
        """
        self._log_method_start("_load_subgenres")
        
        if self.data_path:
            data_file = self.data_path / "subgenres.json"
        else:
            data_file = Path(__file__).parent.parent / "data" / "subgenres.json"
        
        logger.debug(f"Loading subgenres from {data_file}")
        
        try:
            with open(data_file, "r") as f:
                data = json.load(f)
                
            # Log at SUPERDEBUG level
            logger.superdebug(f"Loaded subgenres raw data: {json.dumps(data, indent=2)}")
            
            genres_count = len(data)
            total_subgenres = sum(len(subgenres) for subgenres in data.values())
            logger.debug(f"Loaded {genres_count} genres with {total_subgenres} total subgenres")
            
            self._log_method_end("_load_subgenres", result=f"{genres_count} genres, {total_subgenres} subgenres")
            return data
            
        except FileNotFoundError:
            logger.error(f"Subgenres file not found at {data_file}")
            self._log_method_error("_load_subgenres", FileNotFoundError(f"Subgenres file not found at {data_file}"))
            raise
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in subgenres file: {e}")
            self._log_method_error("_load_subgenres", e)
            raise

    def select_genre(self, genre: Optional[str] = None) -> Tuple[str, str]:
        """Select a genre and subgenre.
        
        If a specific genre is provided, attempts to find it in the available subgenres.
        If no genre is provided or the specified genre is not found, selects a random
        genre from the available options.
        
        Args:
            genre: Optional specific genre to use. If None, randomly selects one.
            
        Returns:
            Tuple of (main_genre, subgenre)
        """
        self._log_method_start("select_genre", genre=genre)
        
        if genre:
            logger.info(f"Attempting to find specified genre: {genre}")
            # If genre is specified, find it in our subgenres
            for main_genre, subgenres in self.subgenres.items():
                logger.superdebug(f"Checking {main_genre} category for {genre}")
                if genre.lower() in [s.lower() for s in subgenres]:
                    logger.info(f"Found specified genre: {genre} (category: {main_genre})")
                    self._log_method_end("select_genre", result=(main_genre, genre))
                    return main_genre, genre
            
            logger.warning(f"Specified genre '{genre}' not found, falling back to random selection")
        
        # Random selection
        main_genres = list(self.subgenres.keys())
        logger.superdebug(f"Available main genres for random selection: {main_genres}")
        
        main_genre = random.choice(main_genres)
        logger.debug(f"Randomly selected main genre: {main_genre}")
        
        available_subgenres = self.subgenres[main_genre]
        logger.superdebug(f"Available subgenres for {main_genre}: {available_subgenres}")
        
        subgenre = random.choice(available_subgenres)
        # Log at INFO level as specified in the requirements
        logger.info(f"Selected random genre: {subgenre} ({main_genre})")
        
        self._log_method_end("select_genre", result=(main_genre, subgenre))
        return main_genre, subgenre

    async def _get_llm_response(self, prompt: str) -> str:
        """Get a response from the LLM.
        
        This is a wrapper around LLMConfig.get_completion for more robust error handling.
        
        Args:
            prompt: Prompt to send to the LLM
            
        Returns:
            Response from the LLM
            
        Raises:
            Exception: If there's an error getting the response
        """
        try:
            response = await self.llm_config.get_completion(prompt)
            
            # Check if the response might be JSON (for backward compatibility with tests)
            if response.strip().startswith('{') and response.strip().endswith('}'):
                try:
                    # This might be a JSON string from a test
                    parsed = json.loads(response)
                    logger.debug("Detected JSON response format")
                    return response
                except json.JSONDecodeError:
                    # Not valid JSON, treat as regular text
                    pass
                    
            return response
        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}")
            self._log_method_error("_get_llm_response", e)
            raise
            
    async def generate_tone_and_themes(self, genre: str, subgenre: str) -> Tuple[str, List[str]]:
        """Generate tone and themes for the story.
        
        Uses the LLM to generate an appropriate tone and set of themes that align
        with the selected genre and subgenre.
        
        Args:
            genre: Main genre category
            subgenre: Specific subgenre
            
        Returns:
            Tuple of (tone, list_of_themes)
        """
        self._log_method_start("generate_tone_and_themes", genre=genre, subgenre=subgenre)
        
        logger.info(f"Generating tone and themes for {subgenre} ({genre})")
        
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
        logger.debug(f"Sending tone/themes prompt to LLM")
        logger.superdebug(f"Full tone/themes prompt:\n{prompt}")
        
        response = await self._get_llm_response(prompt)
        logger.debug("Received tone/themes response from LLM")
        
        # Check if response might be JSON from test mocks
        if response.strip().startswith('{') and response.strip().endswith('}'):
            try:
                parsed_json = json.loads(response)
                if isinstance(parsed_json, dict) and "tone" in parsed_json and "themes" in parsed_json:
                    logger.debug("Parsed JSON response for tone and themes")
                    logger.info(f"Generated tone: {parsed_json['tone']}")
                    logger.info(f"Generated {len(parsed_json['themes'])} themes")
                    self._log_method_end("generate_tone_and_themes")
                    return parsed_json["tone"], parsed_json["themes"]
            except json.JSONDecodeError:
                # Not valid JSON, continue with markdown parsing
                pass
        
        # Parse the markdown response
        tone = ""
        themes = []
        
        current_section = None
        capturing_tone = False
        
        logger.debug("Parsing tone and themes from LLM response")
        for i, line in enumerate(response.split('\n')):
            line = line.strip()
            if not line:
                continue
                
            logger.superdebug(f"Parsing line {i+1}: {line}")
                
            if line.startswith('## Tone'):
                logger.debug("Found tone section")
                current_section = 'tone'
                capturing_tone = True
            elif line.startswith('## Themes'):
                logger.debug("Found themes section")
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
                logger.superdebug(f"Adding to tone: {line}")
            elif current_section == 'themes' and line.startswith('-'):
                theme = line[1:].strip()
                if theme:
                    themes.append(theme)
                    logger.superdebug(f"Found theme: {theme}")
        
        if not tone or not themes:
            error_msg = "Failed to parse tone and themes from response"
            logger.error(f"{error_msg}: {response}")
            self._log_method_error("generate_tone_and_themes", ValueError(error_msg))
            raise ValueError(error_msg)
            
        logger.info(f"Generated tone: {tone}")
        logger.info(f"Generated {len(themes)} themes")
        self._log_method_end("generate_tone_and_themes")
        return tone, themes

    async def process(
        self, 
        genre: Optional[str] = None,
        tone: Optional[str] = None,
        themes: Optional[List[str]] = None
    ) -> Dict:
        """Process genre selection and tone/themes generation.
        
        Main entry point for this agent. Handles the entire workflow of selecting
        a genre and generating appropriate tone and themes.
        
        Args:
            genre: Optional specific genre to use. If None, randomly selects one.
            tone: Optional specific tone to use. If None, generates one.
            themes: Optional specific themes to use. If None, generates them.
            
        Returns:
            Dict containing the selected genre, tone, and themes
        """
        self._log_method_start("process", genre=genre, tone=tone, themes=themes)
        logger.info("Starting genre and vibe generation process")
        
        try:
            # Step 1: Select genre
            logger.debug("Selecting genre")
            main_genre, subgenre = self.select_genre(genre)
            logger.info(f"Selected genre: {main_genre}, subgenre: {subgenre}")
            
            # Step 2: Handle tone and themes based on input
            # Use provided tone and themes or generate them
            if tone and themes:
                logger.info(f"Using provided tone and themes")
                logger.debug(f"Tone: {tone}")
                logger.debug(f"Themes: {themes}")
            elif tone:
                logger.info(f"Using provided tone, generating themes")
                logger.debug(f"Tone: {tone}")
                _, themes = await self.generate_tone_and_themes(main_genre, subgenre)
            elif themes:
                logger.info(f"Using provided themes, generating tone")
                logger.debug(f"Themes: {themes}")
                tone, _ = await self.generate_tone_and_themes(main_genre, subgenre)
            else:
                # Generate tone and themes
                logger.debug("Generating tone and themes")
                tone, themes = await self.generate_tone_and_themes(main_genre, subgenre)
            
            # Create result dictionary
            result = {
                "status": "success",
                "genre": main_genre,
                "subgenre": subgenre,
                "tone": tone,
                "themes": themes
            }
            
            logger.info(f"Successfully generated genre and vibe: {subgenre} with {len(themes)} themes")
            logger.superdebug(f"Complete result: {result}")
            
            self._log_method_end("process", result=result)
            return result
            
        except Exception as e:
            logger.error(f"Error in genre and vibe generation: {str(e)}")
            self._log_method_error("process", e)
            
            return {
                "status": "error",
                "error": str(e)
            } 