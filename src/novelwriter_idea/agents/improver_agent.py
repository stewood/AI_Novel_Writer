"""Improver Agent for enhancing story pitches."""

import logging
from typing import Dict, List, Any

from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ImproverAgent(BaseAgent):
    """Agent responsible for improving story pitches."""

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Improver Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Improver Agent")

    async def improve_pitch(
        self,
        pitch: Dict[str, str],
        evaluation: Dict[str, Any],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> Dict[str, Any]:
        """Improve a story pitch based on evaluation feedback.
        
        Args:
            pitch: The original story pitch
            evaluation: The critic's evaluation
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired emotional/narrative tone
            themes: List of core themes to explore
            
        Returns:
            Dict containing the improved pitch
        """
        prompt = f"""Improve this story pitch for a {subgenre} story in the {genre} genre.

The story should have this tone: {tone}

And explore these themes:
{chr(10).join(f'- {theme}' for theme in themes)}

Here's the original pitch:

# Original Pitch
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

Here's the evaluation:

# Evaluation
## Scores
{chr(10).join(f'- {name}: {score}' for name, score in evaluation["scores"].items())}

## Key Strengths
{chr(10).join(f'- {strength}' for strength in evaluation["key_strengths"])}

## Areas for Improvement
{chr(10).join(f'- {area}' for area in evaluation["areas_for_improvement"])}

Please improve the pitch while:
1. Maintaining its core strengths
2. Addressing the areas for improvement
3. Keeping the tone and themes consistent
4. Making it more compelling and unique

Return your response in this format:

# Improved Pitch
## Title
[Title]

## Hook
[Hook]

## Premise
[Premise]

## Main Conflict
[Main Conflict]

## Unique Twist
[Unique Twist]

## Improvements Made
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

## Elements Preserved
- [Element 1]
- [Element 2]
- [Element 3]
"""

        response = await self._get_llm_response(prompt)
        self.logger.debug(f"Raw LLM response: {response}")
        
        # Parse the markdown response
        improved_pitch = {}
        current_section = None
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('## '):
                current_section = line[3:].lower()
                if current_section in ['improvements made', 'elements preserved']:
                    improved_pitch[current_section] = []
            elif current_section:
                if current_section in ['improvements made', 'elements preserved']:
                    if line.startswith('- '):
                        improved_pitch[current_section].append(line[2:].strip())
                else:
                    if current_section not in improved_pitch:
                        improved_pitch[current_section] = line
                    else:
                        improved_pitch[current_section] += f"\n{line}"
        
        if not improved_pitch:
            raise ValueError("No improved pitch found in response")
            
        self.logger.info(f"Improved pitch: {improved_pitch.get('title', 'Untitled')}")
        self.logger.debug(f"Improvements made: {improved_pitch.get('improvements made', [])}")
        
        return {
            "improved_pitch": improved_pitch
        }

    async def process(
        self,
        pitch: Dict,
        evaluation: Dict,
        genre: str,
        tone: str,
        themes: List[str]
    ) -> Dict:
        """Improve a story pitch based on critic feedback."""
        self.logger.info(f"Improving pitch: {pitch['title']}")
        self.logger.debug(f"Original evaluation scores: {evaluation['scores']}")
        
        # Extract areas needing improvement
        low_scores = {k: v for k, v in evaluation["scores"].items() if v < 8}
        
        prompt = f"""Improve this {genre} story pitch based on the following feedback:

Original Pitch:
Title: {pitch['title']}
Hook: {pitch['hook']}
Premise: {pitch['premise']}
Main Conflict: {pitch['main_conflict']}
Unique Twist: {pitch['unique_twist']}

The story should have a {tone} tone and explore these themes: {', '.join(themes)}.

Critic's Feedback:
Strengths: {', '.join(evaluation['strengths'])}
Weaknesses: {', '.join(evaluation['weaknesses'])}
Improvement Suggestions: {', '.join(evaluation['improvement_suggestions'])}

Areas needing most improvement: {', '.join(low_scores.keys())}

Return your response in this format:

# Improved Pitch

## Title
[Improved title here]

## Hook
[Improved hook here]

## Premise
[Improved premise here]

## Main Conflict
[Improved main conflict here]

## Unique Twist
[Improved unique twist here]

## Improvements Made
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

## Elements Preserved
- [Key element 1]
- [Key element 2]
- [Key element 3]

Make sure the improvements address the weaknesses while maintaining the strengths.
Focus especially on improving: {', '.join(low_scores.keys())}
"""
        
        try:
            self.logger.debug("Sending prompt to LLM for pitch improvement")
            response = await self._get_llm_response(prompt)
            
            # Parse the markdown response
            improved_pitch = {}
            improvements_made = []
            elements_preserved = []
            
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('## Title'):
                    improved_pitch['title'] = next(lines).strip()
                elif line.startswith('## Hook'):
                    improved_pitch['hook'] = next(lines).strip()
                elif line.startswith('## Premise'):
                    improved_pitch['premise'] = next(lines).strip()
                elif line.startswith('## Main Conflict'):
                    improved_pitch['main_conflict'] = next(lines).strip()
                elif line.startswith('## Unique Twist'):
                    improved_pitch['unique_twist'] = next(lines).strip()
                elif line.startswith('## Improvements Made'):
                    while True:
                        improvement = next(lines, '').strip()
                        if not improvement or improvement.startswith('##'):
                            break
                        if improvement.startswith('-'):
                            improvements_made.append(improvement[1:].strip())
                elif line.startswith('## Elements Preserved'):
                    while True:
                        element = next(lines, '').strip()
                        if not element or element.startswith('##'):
                            break
                        if element.startswith('-'):
                            elements_preserved.append(element[1:].strip())
            
            if not improved_pitch:
                raise ValueError("No improved pitch found in response")
            
            self.logger.info(f"Successfully improved pitch: {improved_pitch['title']}")
            self.logger.debug(f"Improvements made: {improvements_made}")
            
            return {
                "status": "success",
                "original_title": pitch["title"],
                "improved_pitch": improved_pitch,
                "improvements_made": improvements_made,
                "elements_preserved": elements_preserved
            }
            
        except Exception as e:
            self.logger.error(f"Error improving pitch: {e}", exc_info=True)
            raise 