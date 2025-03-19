"""Tropemaster Agent for analyzing and improving story tropes."""

import json
import logging
from typing import Dict, List, Optional

from novelwriter_idea.agents.base_agent import BaseAgent

class TropemasterAgent(BaseAgent):
    """Agent responsible for analyzing and improving story tropes."""
    
    def __init__(
        self,
        llm_config: Optional[Dict] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the Tropemaster Agent.
        
        Args:
            llm_config: Configuration for the LLM client
            logger: Optional logger instance
        """
        super().__init__(llm_config, logger)
        self.logger.info("Initializing Tropemaster Agent")
    
    async def process(
        self,
        pitch: Dict,
        genre: str,
        tone: str,
        themes: List[str]
    ) -> Dict:
        """Analyze story tropes and suggest original twists.
        
        Args:
            pitch: The story pitch to analyze
            genre: The story's genre
            tone: The story's tone
            themes: List of story themes
            
        Returns:
            Dict containing trope analysis and suggestions
        """
        self.logger.info(f"Analyzing tropes for: {pitch['title']}")
        
        prompt = f"""Analyze the tropes in this {genre} story pitch and suggest original twists:

Title: {pitch['title']}
Hook: {pitch['hook']}
Concept: {pitch['concept']}
Conflict: {pitch['conflict']}
Twist: {pitch['twist']}

The story should have a {tone} tone and explore these themes: {', '.join(themes)}.

Analyze:
1. Common tropes present in the story
2. How these tropes are currently used
3. Potential ways to subvert or reinvent these tropes
4. Original elements that could be enhanced
5. Genre-specific trope expectations and how to play with them

Format your response as JSON:
{{
    "identified_tropes": [
        {{
            "trope": "name of trope",
            "description": "how it appears in the story",
            "common_usage": "how this trope is typically used",
            "current_handling": "how the story currently handles it",
            "originality_score": 1-10
        }},
        ...
    ],
    "subversion_suggestions": [
        {{
            "trope": "name of trope",
            "suggestion": "how to subvert or reinvent it",
            "impact": "potential impact on story"
        }},
        ...
    ],
    "original_elements": [
        "unique element 1",
        "unique element 2",
        ...
    ],
    "enhancement_suggestions": [
        {{
            "element": "story element to enhance",
            "suggestion": "how to make it more unique",
            "rationale": "why this would work"
        }},
        ...
    ]
}}
"""
        
        try:
            self.logger.debug("Sending prompt to LLM for trope analysis")
            response = self._get_completion(prompt)
            
            # Parse the response
            analysis = json.loads(response)
            
            self.logger.info(f"Completed trope analysis for: {pitch['title']}")
            self.logger.debug(f"Found {len(analysis['identified_tropes'])} tropes")
            
            return {
                "status": "success",
                "title": pitch["title"],
                "analysis": analysis
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error analyzing tropes: {e}", exc_info=True)
            raise 