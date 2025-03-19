"""Pitch Generator Agent for novel idea generation.

This agent is responsible for generating multiple compelling story pitches 
based on provided genre, tone, and themes. It structures each pitch with a 
title, hook, premise, main conflict, and unique twist.
"""

import logging
import re
from typing import Dict, List, Any

from novel_writer.config.llm import LLMConfig
from novel_writer.agents.base_agent import BaseAgent

# Initialize logger
logger = logging.getLogger(__name__)

class PitchGeneratorAgent(BaseAgent):
    """Agent responsible for generating story pitches.
    
    This agent creates multiple story pitches based on provided genre 
    information, tone, and themes. Each pitch includes a title, hook,
    premise, main conflict, and unique twist element.
    """

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Pitch Generator Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Pitch Generator Agent")

    async def generate_pitches(
        self,
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> List[Dict[str, str]]:
        """Generate multiple story pitches.
        
        Creates 3 distinct story pitches based on the provided genre, tone,
        and themes. Each pitch includes a title, hook, premise, main conflict,
        and unique twist.
        
        Args:
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            List of dictionaries, each containing a complete story pitch
        """
        self._log_method_start(
            "generate_pitches", 
            genre=genre, 
            subgenre=subgenre, 
            tone=tone,
            themes=themes
        )
        
        logger.info(f"Generating pitches for {subgenre} (a type of {genre})")
        logger.debug(f"Using tone: {tone[:50]}..." if len(tone) > 50 else f"Using tone: {tone}")
        logger.debug(f"Using {len(themes)} themes")
        logger.superdebug(f"Full themes list: {themes}")
        
        # Format themes list for prompt
        themes_str = ", ".join(themes)
        logger.debug(f"Formatted themes: {themes_str}")
        
        # Construct prompt for generating pitches
        prompt = f"""
Generate 3 compelling and original story pitches for a {subgenre} story ({genre}).
The story should have a {tone} tone and explore the following themes: {themes_str}.

For each pitch, provide the following:

# Pitch 1
## Title
[Creative and marketable title]

## Hook
[One-sentence hook that captures the core appeal]

## Premise
[2-3 sentences expanding the core concept]

## Main Conflict
[The central conflict or challenge]

## Unique Twist
[What makes this story fresh or unexpected]

# Pitch 2
...

# Pitch 3
...

Make each pitch distinct and compelling, with different premises, conflicts, and twists.
Ensure they fit well within the {subgenre} subgenre while having commercial and artistic potential.
Be specific and concrete rather than vague or generic.
"""
        logger.debug("Sending pitch generation prompt to LLM")
        logger.superdebug(f"Full pitch generation prompt:\n{prompt}")
        
        # Get response from LLM
        response = await self._get_llm_response(prompt)
        logger.info("Received pitch response from LLM")
        logger.superdebug(f"Raw pitch response length: {len(response)} characters")
        
        # Parse response to extract pitches
        logger.debug("Beginning to parse pitches from LLM response")
        pitches = self._parse_pitches_response(response)
        
        # Ensure we have at least one pitch
        if not pitches:
            error_msg = "No valid pitches were generated"
            logger.error(error_msg)
            self._log_method_error("generate_pitches", ValueError(error_msg))
            raise ValueError(error_msg)
        
        num_pitches = len(pitches)
        logger.info(f"Successfully generated {num_pitches} valid story pitches")
        for i, pitch in enumerate(pitches):
            logger.info(f"Pitch {i+1}: {pitch['title']}")
            
        self._log_method_end("generate_pitches", result=f"{num_pitches} pitches")
        return pitches
        
    def _parse_pitches_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the LLM response to extract structured pitches.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            List of dictionaries, each containing a complete story pitch
        """
        logger.debug("Parsing LLM response into structured pitches")
        
        # Split response into individual pitches
        pitch_blocks = re.split(r'#\s*Pitch\s+\d+|---', response)
        # Remove empty blocks
        pitch_blocks = [block.strip() for block in pitch_blocks if block.strip()]
        
        logger.debug(f"Found {len(pitch_blocks)} potential pitch blocks")
        
        pitches = []
        for i, block in enumerate(pitch_blocks):
            logger.debug(f"Processing pitch block {i+1}")
            pitch = {}
            
            # Extract title
            title_match = re.search(r'\*\*Title:\*\*\s*(.*?)(?:\*\*|\n)', block)
            if title_match:
                pitch['title'] = title_match.group(1).strip()
                logger.debug(f"Extracted title: {pitch['title']}")
            else:
                pitch['title'] = f"Untitled Pitch {i+1}"
                logger.warning(f"No title found for pitch {i+1}, using default")
                
            # Extract hook
            hook_match = re.search(r'\*\*Hook:\*\*\s*(.*?)(?:\*\*|\n\n)', block)
            if hook_match:
                pitch['hook'] = hook_match.group(1).strip()
                logger.debug(f"Extracted hook: {pitch['hook'][:30]}...")
            else:
                pitch['hook'] = "[Missing]"
                logger.warning(f"No hook found for pitch {i+1}")
                
            # Extract premise
            premise_match = re.search(r'\*\*Premise:\*\*\s*(.*?)(?:\*\*Main|\*\*Conflict|\n\n\*\*)', block, re.DOTALL)
            if premise_match:
                pitch['premise'] = premise_match.group(1).strip()
                logger.debug(f"Extracted premise: {pitch['premise'][:30]}...")
            else:
                pitch['premise'] = "[Missing]"
                logger.warning(f"No premise found for pitch {i+1}")
                
            # Extract main conflict
            conflict_match = re.search(r'\*\*Main Conflict:\*\*\s*(.*?)(?:\*\*Unique|\*\*Twist|\n\n\*\*)', block, re.DOTALL)
            if conflict_match:
                pitch['main_conflict'] = conflict_match.group(1).strip()
                logger.debug(f"Extracted main conflict: {pitch['main_conflict'][:30]}...")
            else:
                pitch['main_conflict'] = "[Missing]"
                logger.warning(f"No main conflict found for pitch {i+1}")
                
            # Extract unique twist
            twist_match = re.search(r'\*\*Unique Twist:\*\*\s*(.*?)(?:\n\n|$)', block, re.DOTALL)
            if twist_match:
                pitch['unique_twist'] = twist_match.group(1).strip()
                logger.debug(f"Extracted unique twist: {pitch['unique_twist'][:30]}...")
            else:
                pitch['unique_twist'] = "[Missing]"
                logger.warning(f"No unique twist found for pitch {i+1}")
                
            # Check if the pitch is valid (has at least title and one other component)
            missing_sections = [section for section in ['title', 'hook', 'premise', 'main_conflict', 'unique_twist'] 
                               if pitch.get(section) == "[Missing]"]
                               
            if len(missing_sections) >= 4:  # Too many missing sections
                logger.warning(f"Pitch {i+1} missing too many sections ({missing_sections}), skipping")
                logger.superdebug(f"Raw content of invalid pitch block:\n{block[:200]}...")
                continue
                
            logger.debug(f"Validated pitch {i+1}: {pitch['title']}")
            logger.superdebug(f"Full validated pitch {i+1}: {pitch}")
            pitches.append(pitch)
            
        logger.info(f"Successfully extracted {len(pitches)} valid pitches")
        return pitches

    async def process(
        self,
        genre: str,
        tone: str,
        themes: List[str],
        num_pitches: int = 3
    ) -> Dict:
        """Generate multiple story pitches based on genre, tone, and themes."""
        self.logger.info(f"Generating {num_pitches} pitches for {genre} story")
        
        prompt = f"""Generate {num_pitches} unique and compelling story pitches for a {genre} story.
The story should have a {tone} tone and explore these themes: {', '.join(themes)}.

Return your response in this format:

# Story Pitches

## Pitch 1
### Title
[Title here]

### Hook
[One-sentence hook here]

### Premise
[2-3 sentence premise here]

### Main Conflict
[Core conflict here]

### Unique Twist
[What makes this story unique]

## Pitch 2
[Same structure as Pitch 1]

## Pitch 3
[Same structure as Pitch 1]

Be specific and creative. Each pitch should have a unique concept, conflict, and twist.
"""
        self.logger.debug("Sending prompt to LLM for pitch generation")
        response = await self.llm_config.get_completion(prompt)
        self.logger.debug("Received response from LLM")
        
        try:
            # Parse the response and extract the pitches
            pitches = self._parse_pitches_response(response)
            
            self.logger.info(f"Successfully generated {len(pitches)} pitches")
            
            return {
                "status": "success",
                "num_pitches": len(pitches),
                "pitches": pitches
            }
        except Exception as e:
            self.logger.error(f"Error generating pitches: {str(e)}")
            raise 