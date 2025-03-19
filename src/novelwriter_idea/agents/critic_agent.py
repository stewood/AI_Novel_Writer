"""Critic Agent for evaluating story pitches."""

import json
import logging
from typing import Dict, List, Optional

from novelwriter_idea.agents.base_agent import BaseAgent

class CriticAgent(BaseAgent):
    """Agent responsible for evaluating story pitches."""
    
    def __init__(
        self,
        llm_config: Optional[Dict] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the Critic Agent.
        
        Args:
            llm_config: Configuration for the LLM client
            logger: Optional logger instance
        """
        super().__init__(llm_config, logger)
        self.logger.info("Initializing Critic Agent")
    
    async def process(
        self,
        pitches: List[Dict],
        genre: str,
        tone: str,
        themes: List[str]
    ) -> Dict:
        """Evaluate multiple story pitches based on various criteria.
        
        Args:
            pitches: List of story pitches to evaluate
            genre: The target genre
            tone: The target tone
            themes: List of target themes
            
        Returns:
            Dict containing evaluations for each pitch
        """
        self.logger.info(f"Evaluating {len(pitches)} pitches")
        
        evaluations = []
        for i, pitch in enumerate(pitches):
            self.logger.debug(f"Evaluating pitch {i+1}: {pitch['title']}")
            
            prompt = f"""Evaluate this story pitch for a {genre} story:

Title: {pitch['title']}
Hook: {pitch['hook']}
Concept: {pitch['concept']}
Conflict: {pitch['conflict']}
Twist: {pitch['twist']}

The story should have a {tone} tone and explore these themes: {', '.join(themes)}.

Evaluate the pitch on these criteria (score 1-10):
1. Originality: How fresh and unique is the concept?
2. Emotional Impact: How emotionally engaging is the story?
3. Genre Fit: How well does it fit the {genre} genre?
4. Theme Integration: How well does it incorporate the themes?
5. Conflict Strength: How compelling is the central conflict?
6. Hook Quality: How effective is the one-sentence hook?
7. Twist Impact: How surprising and satisfying is the twist?

Format your response as JSON:
{{
    "scores": {{
        "originality": score,
        "emotional_impact": score,
        "genre_fit": score,
        "theme_integration": score,
        "conflict_strength": score,
        "hook_quality": score,
        "twist_impact": score
    }},
    "overall_score": average_score,
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "improvement_suggestions": ["suggestion 1", "suggestion 2"]
}}
"""
            
            try:
                self.logger.debug("Sending prompt to LLM for evaluation")
                response = self._get_completion(prompt)
                
                # Parse the response
                evaluation = json.loads(response)
                evaluation["title"] = pitch["title"]
                evaluations.append(evaluation)
                
                self.logger.debug(f"Evaluation complete for '{pitch['title']}' with overall score {evaluation['overall_score']}")
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse LLM response as JSON: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Error evaluating pitch: {e}", exc_info=True)
                raise
        
        # Sort evaluations by overall score
        evaluations.sort(key=lambda x: x["overall_score"], reverse=True)
        
        self.logger.info("Successfully evaluated all pitches")
        return {
            "status": "success",
            "evaluations": evaluations
        } 