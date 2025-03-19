"""Voter Agent for selecting the best story pitch."""

import json
import logging
from typing import Dict, List, Optional

from novelwriter_idea.agents.base_agent import BaseAgent

class VoterAgent(BaseAgent):
    """Agent responsible for selecting the best story pitch."""
    
    def __init__(
        self,
        llm_config: Optional[Dict] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the Voter Agent.
        
        Args:
            llm_config: Configuration for the LLM client
            logger: Optional logger instance
        """
        super().__init__(llm_config, logger)
        self.logger.info("Initializing Voter Agent")
    
    async def process(
        self,
        pitches: List[Dict],
        evaluations: List[Dict],
        genre: str,
        tone: str,
        themes: List[str]
    ) -> Dict:
        """Select the best story pitch based on evaluations and additional analysis.
        
        Args:
            pitches: List of story pitches (original and improved)
            evaluations: List of evaluations for each pitch
            genre: The target genre
            tone: The target tone
            themes: List of target themes
            
        Returns:
            Dict containing the selected pitch and rationale
        """
        self.logger.info(f"Selecting best pitch from {len(pitches)} candidates")
        
        # Prepare pitch summaries for comparison
        pitch_summaries = []
        for i, (pitch, eval) in enumerate(zip(pitches, evaluations)):
            summary = {
                "index": i,
                "title": pitch["title"],
                "overall_score": eval["overall_score"],
                "strengths": eval["strengths"],
                "weaknesses": eval["weaknesses"]
            }
            pitch_summaries.append(summary)
            
        prompt = f"""Select the best story pitch from these candidates for a {genre} story:

The story should have a {tone} tone and explore these themes: {', '.join(themes)}.

Candidates:
{json.dumps(pitch_summaries, indent=2)}

Consider:
1. Overall quality and potential
2. Fit with genre and themes
3. Balance of strengths vs weaknesses
4. Market appeal and target audience
5. Development potential

Format your response as JSON:
{{
    "selected_index": index_of_chosen_pitch,
    "rationale": [
        "reason 1 for selection",
        "reason 2 for selection",
        ...
    ],
    "potential_challenges": [
        "challenge 1 to consider",
        "challenge 2 to consider",
        ...
    ],
    "development_recommendations": [
        "recommendation 1",
        "recommendation 2",
        ...
    ]
}}
"""
        
        try:
            self.logger.debug("Sending prompt to LLM for pitch selection")
            response = self._get_completion(prompt)
            
            # Parse the response
            selection = json.loads(response)
            selected_pitch = pitches[selection["selected_index"]]
            
            self.logger.info(f"Selected pitch: {selected_pitch['title']}")
            self.logger.debug(f"Selection rationale: {selection['rationale']}")
            
            return {
                "status": "success",
                "selected_pitch": selected_pitch,
                "selection_details": selection
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error selecting pitch: {e}", exc_info=True)
            raise 