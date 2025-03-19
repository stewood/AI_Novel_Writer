"""Voter Agent for selecting the best story pitch."""

import logging
from typing import Dict, List, Any

from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class VoterAgent(BaseAgent):
    """Agent responsible for selecting the best story pitch."""

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Voter Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Voter Agent")

    def _format_pitches_and_evaluations(self, pitches, evaluations):
        """Format pitches and evaluations for the prompt."""
        formatted = []
        for i, (pitch, evaluation) in enumerate(zip(pitches, evaluations)):
            formatted.append(f"""# Pitch {i+1}
## Title
{pitch["title"]}

## Hook
{pitch["hook"]}

## Premise
{pitch["premise"]}

## Main Conflict
{pitch["main_conflict"]}

## Unique Twist
{pitch["unique_twist"]}

## Evaluation
### Scores
{chr(10).join(f"- {name}: {score}" for name, score in evaluation["scores"].items())}

### Key Strengths
{chr(10).join(f"- {strength}" for strength in evaluation["key_strengths"])}

### Areas for Improvement
{chr(10).join(f"- {area}" for area in evaluation["areas_for_improvement"])}
""")
        return "\n".join(formatted)

    async def select_best_pitch(
        self,
        pitches: List[Dict[str, str]],
        evaluations: List[Dict[str, Any]],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> Dict[str, Any]:
        """Select the best story pitch based on evaluations.
        
        Args:
            pitches: List of story pitches
            evaluations: List of pitch evaluations
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired emotional/narrative tone
            themes: List of core themes to explore
            
        Returns:
            Dict containing the selected pitch and rationale
        """
        prompt = f"""
Given the following pitches and evaluations, select the best pitch for a {genre} story.

{self._format_pitches_and_evaluations(pitches, evaluations)}

Please provide your selection in the following format:

# Selection
## Winner
[Title of winning pitch]

## Selection Criteria
[List key reasons for selection, considering quality, genre fit, themes, etc.]

## Development Recommendations
[List specific suggestions to strengthen the winning pitch]

## Potential Challenges
[List potential difficulties in executing the winning pitch]
"""

        response = await self._get_llm_response(prompt)
        self.logger.debug(f"Raw LLM response: {response}")
        
        # Parse response
        selection = {
            'winner': None,
            'selection_criteria': [],
            'development_recommendations': [],
            'potential_challenges': []
        }

        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('## '):
                section = line[3:].lower()
                if section == 'winner':
                    current_section = 'winner'
                elif section == 'selection criteria':
                    current_section = 'selection_criteria'
                elif section == 'development recommendations':
                    current_section = 'development_recommendations'
                elif section == 'potential challenges':
                    current_section = 'potential_challenges'
            elif current_section:
                if current_section == 'winner':
                    selection['winner'] = line
                elif line.startswith('- '):
                    selection[current_section].append(line[2:].strip())

        if not selection['winner']:
            raise ValueError("No winner found in response")
            
        self.logger.info(f"Selected pitch: {selection['winner']}")
        self.logger.debug(f"Selection criteria: {selection['selection_criteria']}")
        
        return selection 