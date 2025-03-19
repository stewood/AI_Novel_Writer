"""Critic Agent for evaluating story pitches."""

import logging
from typing import Dict, List, Any

from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CriticAgent(BaseAgent):
    """Agent responsible for evaluating story pitches."""

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Critic Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Critic Agent")

    async def evaluate_pitches(
        self,
        pitches: List[Dict[str, str]],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> Dict[str, Any]:
        """Evaluate multiple story pitches.
        
        Args:
            pitches: List of story pitches to evaluate
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired emotional/narrative tone
            themes: List of core themes to explore
            
        Returns:
            Dict containing the evaluations
        """
        prompt = f"""Evaluate these story pitches for a {subgenre} story in the {genre} genre.

The story should have this tone: {tone}

And explore these themes:
{chr(10).join(f'- {theme}' for theme in themes)}

For each pitch, evaluate:
1. Originality (1-10)
2. Emotional Impact (1-10)
3. Genre Fit (1-10)
4. Theme Integration (1-10)
5. Commercial Potential (1-10)

Also provide:
- Key Strengths
- Areas for Improvement
- Overall Score (average of all scores)

Here are the pitches to evaluate:

{chr(10).join(f'''# Pitch {i+1}
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
''' for i, pitch in enumerate(pitches))}

Return your response in this format for each pitch:

# Evaluation 1
## Scores
- Originality: [score]
- Emotional Impact: [score]
- Genre Fit: [score]
- Theme Integration: [score]
- Commercial Potential: [score]
- Overall Score: [average]

## Key Strengths
- [Strength 1]
- [Strength 2]
- [Strength 3]

## Areas for Improvement
- [Area 1]
- [Area 2]
- [Area 3]

# Evaluation 2
[Same format]

# Evaluation 3
[Same format]
"""

        response = await self._get_llm_response(prompt)
        self.logger.debug(f"Raw LLM response: {response}")
        
        # Parse the markdown response
        evaluations = []
        current_eval = {}
        current_section = None
        current_subsection = None
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('# Evaluation'):
                if current_eval:
                    evaluations.append(current_eval)
                current_eval = {
                    'scores': {},
                    'key_strengths': [],
                    'areas_for_improvement': []
                }
            elif line.startswith('## '):
                current_section = line[3:].lower()
                current_subsection = None
            elif line.startswith('- '):
                if current_section == 'scores':
                    score_line = line[2:].split(':')
                    if len(score_line) == 2:
                        score_name = score_line[0].strip().lower()
                        try:
                            score_value = float(score_line[1].strip())
                            current_eval['scores'][score_name] = score_value
                        except ValueError:
                            self.logger.warning(f"Could not parse score: {line}")
                elif current_section == 'key strengths':
                    current_eval['key_strengths'].append(line[2:].strip())
                elif current_section == 'areas for improvement':
                    current_eval['areas_for_improvement'].append(line[2:].strip())
        
        # Add the last evaluation
        if current_eval:
            evaluations.append(current_eval)
            
        if not evaluations:
            raise ValueError("No evaluations found in response")
            
        self.logger.info(f"Generated {len(evaluations)} evaluations")
        self.logger.debug(f"Evaluation scores: {[e['scores'].get('overall score', 0) for e in evaluations]}")
        
        return {
            "evaluations": evaluations
        } 