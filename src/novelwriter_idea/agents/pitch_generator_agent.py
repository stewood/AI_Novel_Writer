"""Pitch Generator Agent for generating story pitches."""

import json
import logging
from typing import Dict, List, Optional

from novelwriter_idea.agents.base_agent import BaseAgent

class PitchGeneratorAgent(BaseAgent):
    """Agent responsible for generating story pitches."""
    
    def __init__(
        self,
        llm_config: Optional[Dict] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the Pitch Generator Agent.
        
        Args:
            llm_config: Configuration for the LLM client
            logger: Optional logger instance
        """
        super().__init__(llm_config, logger)
        self.logger.info("Initializing Pitch Generator Agent")
    
    async def process(
        self,
        genre: str,
        tone: str,
        themes: List[str],
        num_pitches: int = 3
    ) -> Dict:
        """Generate multiple story pitches based on genre, tone, and themes.
        
        Args:
            genre: The story's genre
            tone: The story's tone
            themes: List of story themes
            num_pitches: Number of pitches to generate (default: 3)
            
        Returns:
            Dict containing the generated pitches and metadata
        """
        self.logger.info(f"Generating {num_pitches} pitches for {genre} story")
        
        prompt = f"""Generate {num_pitches} unique and compelling story pitches for a {genre} story.
        The story should have a {tone} tone and explore these themes: {', '.join(themes)}.
        
        For each pitch, provide:
        1. A catchy title
        2. A one-sentence hook
        3. A brief paragraph expanding on the concept
        4. The main conflict
        5. A unique twist or element
        
        Format your response as JSON:
        {{
            "pitches": [
                {{
                    "title": "Title here",
                    "hook": "One-sentence hook here",
                    "concept": "Expanded concept here",
                    "conflict": "Main conflict here",
                    "twist": "Unique twist here"
                }},
                // ... more pitches ...
            ]
        }}
        """
        
        try:
            self.logger.debug("Sending prompt to LLM for pitch generation")
            response = self._get_completion(prompt)
            
            # Parse the response
            pitches_data = json.loads(response)
            pitches = pitches_data.get("pitches", [])
            
            if not pitches:
                raise ValueError("No pitches generated in response")
            
            self.logger.info(f"Successfully generated {len(pitches)} pitches")
            
            return {
                "status": "success",
                "num_pitches": len(pitches),
                "pitches": pitches
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error generating pitches: {e}", exc_info=True)
            raise 