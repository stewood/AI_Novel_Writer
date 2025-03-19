"""Tropemaster Agent for analyzing and suggesting trope twists."""

import logging
from typing import Dict, Any

from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class TropemasterAgent(BaseAgent):
    """Agent responsible for analyzing tropes and suggesting original twists."""

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Tropemaster Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Tropemaster Agent")

    async def analyze_tropes(
        self,
        pitch: Dict[str, Any],  # Changed from str to Dict to match our data structure
        genre: str,
        subgenre: str
    ) -> Dict[str, Any]:
        """Analyze tropes in a story pitch and suggest original twists.
        
        Args:
            pitch: Dictionary containing the pitch details
            genre: Main genre category
            subgenre: Specific subgenre
            
        Returns:
            Dictionary with analysis results
        """
        # Format the pitch for the prompt
        formatted_pitch = f"""
Title: {pitch['title']}

Hook: {pitch['hook']}

Premise: {pitch['premise']}

Main Conflict: {pitch['main_conflict']}

Unique Twist: {pitch['unique_twist']}
"""

        prompt = f"""
You are a trope analysis expert. Please analyze the following {subgenre} story pitch and identify common tropes, suggest original twists, and highlight unique elements.

# Story Pitch
{formatted_pitch}

Please provide your analysis in the following format:

# Trope Analysis
## Detected Tropes
- [List at least 3-5 common tropes found in the pitch]

## Suggested Twists
- [List at least 3 suggestions for making the tropes more original]

## Original Elements
- [List elements that are already unique and fresh]

## Enhancement Suggestions
- [List ways to further strengthen the story's originality]
"""

        response = await self._get_llm_response(prompt)
        self.logger.debug(f"Raw LLM response: {response}")

        # Parse response
        analysis = {
            'detected_tropes': [],
            'suggested_twists': [],
            'original_elements': [],
            'enhancement_suggestions': []
        }

        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('## '):
                section = line[3:].lower()
                if section == 'detected tropes':
                    current_section = 'detected_tropes'
                elif section == 'suggested twists':
                    current_section = 'suggested_twists'
                elif section == 'original elements':
                    current_section = 'original_elements'
                elif section == 'enhancement suggestions':
                    current_section = 'enhancement_suggestions'
            elif current_section and line.startswith('- '):
                analysis[current_section].append(line[2:].strip())

        # If no tropes were found, add a default one to prevent errors
        if not analysis['detected_tropes']:
            self.logger.warning("No tropes found in response, adding default trope entry")
            analysis['detected_tropes'].append("Standard genre conventions")
            
        # Ensure we have elements in each section
        for section in analysis:
            if not analysis[section]:
                self.logger.warning(f"No items found for {section}, adding default entry")
                analysis[section].append("Further analysis needed")

        self.logger.info(f"Found {len(analysis['detected_tropes'])} tropes")
        self.logger.debug(f"Suggested twists: {analysis['suggested_twists']}")

        return analysis 