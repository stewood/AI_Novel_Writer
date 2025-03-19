"""Pitch Generator Agent for novel idea generation."""

import logging
from typing import Dict, List, Any

from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class PitchGeneratorAgent(BaseAgent):
    """Agent responsible for generating story pitches."""

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
    ) -> Dict[str, Any]:
        """Generate multiple story pitches.
        
        Args:
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired emotional/narrative tone
            themes: List of core themes to explore
            
        Returns:
            Dict containing the generated pitches
        """
        prompt = f"""Generate 3 unique story pitches for a {subgenre} story in the {genre} genre.

The story should have this tone: {tone}

And explore these themes:
{chr(10).join(f'- {theme}' for theme in themes)}

For each pitch, provide:
1. A compelling title
2. A one-sentence hook that captures the core conflict
3. A brief premise (2-3 sentences)
4. The main conflict
5. A unique twist

Return your response in this format:

# Pitch 1
## Title
[Title]

## Hook
[Hook]

## Premise
[Premise]

## Main Conflict
[Conflict]

## Unique Twist
[Twist]

# Pitch 2
[Same format]

# Pitch 3
[Same format]

Make each pitch distinct and compelling, with clear hooks and unique twists.
"""

        response = await self._get_llm_response(prompt)
        self.logger.debug(f"Raw LLM response: {response}")
        
        # Parse the markdown response
        pitches = []
        current_pitch = {}
        current_section = None
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('# Pitch'):
                if current_pitch:
                    # Rename keys to match expected format
                    if 'main conflict' in current_pitch:
                        current_pitch['main_conflict'] = current_pitch.pop('main conflict')
                    if 'unique twist' in current_pitch:
                        current_pitch['unique_twist'] = current_pitch.pop('unique twist')
                    pitches.append(current_pitch)
                current_pitch = {}
            elif line.startswith('## '):
                current_section = line[3:].lower()
            elif current_section:
                if current_section not in current_pitch:
                    current_pitch[current_section] = line
                else:
                    current_pitch[current_section] += f"\n{line}"
        
        # Add the last pitch
        if current_pitch:
            # Rename keys to match expected format
            if 'main conflict' in current_pitch:
                current_pitch['main_conflict'] = current_pitch.pop('main conflict')
            if 'unique twist' in current_pitch:
                current_pitch['unique_twist'] = current_pitch.pop('unique twist')
            pitches.append(current_pitch)
            
        if not pitches:
            raise ValueError("No pitches found in response")
            
        self.logger.info(f"Generated {len(pitches)} pitches")
        self.logger.debug(f"Pitch titles: {[p.get('title', 'Untitled') for p in pitches]}")
        
        return {
            "pitches": pitches
        }

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

Make each pitch distinct and compelling, with clear hooks and unique twists.
"""
        
        try:
            self.logger.debug("Sending prompt to LLM for pitch generation")
            response = await self._get_llm_response(prompt)
            
            # Parse the markdown response
            pitches = []
            current_pitch = {}
            
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('## Pitch'):
                    if current_pitch:
                        pitches.append(current_pitch)
                    current_pitch = {}
                elif line.startswith('### Title'):
                    current_pitch['title'] = next(lines).strip()
                elif line.startswith('### Hook'):
                    current_pitch['hook'] = next(lines).strip()
                elif line.startswith('### Premise'):
                    current_pitch['premise'] = next(lines).strip()
                elif line.startswith('### Main Conflict'):
                    current_pitch['main_conflict'] = next(lines).strip()
                elif line.startswith('### Unique Twist'):
                    current_pitch['unique_twist'] = next(lines).strip()
            
            if current_pitch:
                pitches.append(current_pitch)
            
            if not pitches:
                raise ValueError("No pitches found in response")
            
            self.logger.info(f"Generated {len(pitches)} pitches")
            for pitch in pitches:
                self.logger.debug(f"Pitch title: {pitch.get('title', 'Untitled')}")
            
            return {
                "status": "success",
                "pitches": pitches
            }
            
        except Exception as e:
            self.logger.error(f"Error generating pitches: {e}", exc_info=True)
            raise 