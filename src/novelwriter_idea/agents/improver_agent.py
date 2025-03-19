"""Improver Agent for enhancing story pitches based on feedback."""

import json
import logging
from typing import Dict, List, Optional

from novelwriter_idea.agents.base_agent import BaseAgent

class ImproverAgent(BaseAgent):
    """Agent responsible for improving story pitches based on critic feedback."""
    
    def __init__(
        self,
        llm_config: Optional[Dict] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the Improver Agent.
        
        Args:
            llm_config: Configuration for the LLM client
            logger: Optional logger instance
        """
        super().__init__(llm_config, logger)
        self.logger.info("Initializing Improver Agent")
    
    async def process(
        self,
        pitch: Dict,
        evaluation: Dict,
        genre: str,
        tone: str,
        themes: List[str]
    ) -> Dict:
        """Improve a story pitch based on critic feedback.
        
        Args:
            pitch: Original story pitch
            evaluation: Critic's evaluation of the pitch
            genre: The target genre
            tone: The target tone
            themes: List of target themes
            
        Returns:
            Dict containing the improved pitch
        """
        self.logger.info(f"Improving pitch: {pitch['title']}")
        self.logger.debug(f"Original evaluation scores: {evaluation['scores']}")
        
        # Extract areas needing improvement
        low_scores = {k: v for k, v in evaluation["scores"].items() if v < 8}
        
        prompt = f"""Improve this {genre} story pitch based on the following feedback:

Original Pitch:
Title: {pitch['title']}
Hook: {pitch['hook']}
Concept: {pitch['concept']}
Conflict: {pitch['conflict']}
Twist: {pitch['twist']}

The story should have a {tone} tone and explore these themes: {', '.join(themes)}.

Critic's Feedback:
Strengths: {', '.join(evaluation['strengths'])}
Weaknesses: {', '.join(evaluation['weaknesses'])}
Improvement Suggestions: {', '.join(evaluation['improvement_suggestions'])}

Areas needing most improvement: {', '.join(low_scores.keys())}

Generate an improved version of this pitch that addresses the weaknesses while maintaining the strengths.
Focus especially on improving: {', '.join(low_scores.keys())}

Format your response as JSON:
{{
    "title": "improved title if needed, otherwise keep original",
    "hook": "improved hook",
    "concept": "improved concept",
    "conflict": "improved conflict",
    "twist": "improved twist",
    "improvements_made": ["list specific improvements made"],
    "elements_preserved": ["list key elements preserved from original"]
}}
"""
        
        try:
            self.logger.debug("Sending prompt to LLM for pitch improvement")
            response = self._get_completion(prompt)
            
            # Parse the response
            improved_pitch = json.loads(response)
            
            self.logger.info(f"Successfully improved pitch: {improved_pitch['title']}")
            self.logger.debug(f"Improvements made: {improved_pitch['improvements_made']}")
            
            return {
                "status": "success",
                "original_title": pitch["title"],
                "improved_pitch": improved_pitch
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error improving pitch: {e}", exc_info=True)
            raise 