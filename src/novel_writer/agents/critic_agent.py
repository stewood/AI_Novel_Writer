"""Critic Agent for evaluating story pitches.

This agent is responsible for evaluating story pitches based on multiple criteria
including originality, emotional impact, genre fit, theme integration,
and commercial potential.
"""

import logging
import re
from typing import Dict, List, Any

from novel_writer.config.llm import LLMConfig
from novel_writer.agents.base_agent import BaseAgent

# Initialize logger
logger = logging.getLogger(__name__)

class CriticAgent(BaseAgent):
    """Agent responsible for evaluating story pitches.
    
    This agent analyzes story pitches against multiple criteria and provides
    detailed feedback on strengths and areas for improvement. It serves as
    the quality control component of the idea generation process.
    """

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
    ) -> List[Dict[str, Any]]:
        """Evaluate multiple story pitches.
        
        Analyzes each pitch against multiple criteria and provides detailed
        feedback on strengths and areas for improvement.
        
        Args:
            pitches: List of story pitches to evaluate
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            List of evaluation dictionaries containing scores and feedback
        """
        self._log_method_start(
            "evaluate_pitches", 
            pitches_count=len(pitches),
            genre=genre,
            subgenre=subgenre,
            themes_count=len(themes)
        )
        
        logger.info(f"Evaluating {len(pitches)} story pitches for {subgenre}")
        logger.debug(f"Using tone: {tone[:50]}..." if len(tone) > 50 else f"Using tone: {tone}")
        logger.debug(f"Using {len(themes)} themes")
        logger.superdebug(f"Full themes list: {themes}")
        
        evaluations = []
        
        # Format themes for the prompt
        themes_str = ", ".join(themes)
        
        # Evaluate each pitch
        for i, pitch in enumerate(pitches):
            pitch_num = i + 1
            logger.info(f"Evaluating pitch {pitch_num}/{len(pitches)}: {pitch.get('title', 'Untitled')}")
            logger.superdebug(f"Full pitch {pitch_num} details: {pitch}")
            
            # Prepare pitch text for evaluation
            pitch_text = self._format_pitch_for_evaluation(pitch)
            logger.debug(f"Formatted pitch {pitch_num} for evaluation, length: {len(pitch_text)} characters")
            logger.superdebug(f"Formatted pitch text:\n{pitch_text}")
            
            # Construct evaluation prompt
            prompt = f"""
Evaluate this story pitch for a {subgenre} story in the {genre} genre.
The story should have a {tone} tone and explore these themes: {themes_str}.

{pitch_text}

Provide a comprehensive evaluation using this format:

# Evaluation
## Scores
- Originality: [1-10]/10
- Emotional Impact: [1-10]/10
- Genre Fit: [1-10]/10
- Theme Integration: [1-10]/10
- Commercial Potential: [1-10]/10
- Overall Score: [calculated average]/10

## Key Strengths
- [Strength 1: Specific observation about what works well]
- [Strength 2: Specific observation about what works well]
- [Strength 3: Specific observation about what works well]

## Areas for Improvement
- [Area 1: Specific suggestion for improvement]
- [Area 2: Specific suggestion for improvement]
- [Area 3: Specific suggestion for improvement]

Be specific, constructive, and honest. Consider the expectations of the {subgenre} genre and how well the themes are integrated.
"""
            logger.debug(f"Sending evaluation prompt for pitch {pitch_num} to LLM")
            logger.superdebug(f"Full evaluation prompt for pitch {pitch_num}:\n{prompt}")
            
            # Get evaluation from LLM
            response = await self._get_llm_response(prompt)
            logger.info(f"Received evaluation response for pitch {pitch_num}")
            logger.superdebug(f"Raw evaluation response length: {len(response)} characters")
            
            # Parse evaluation
            evaluation = self._parse_evaluation(response, pitch_num)
            
            # Add to evaluations list
            evaluations.append(evaluation)
            logger.info(f"Completed evaluation for pitch {pitch_num}")
            
            # Calculate and log the overall score
            if "scores" in evaluation:
                avg_score = sum(evaluation["scores"].values()) / len(evaluation["scores"])
                logger.info(f"Pitch {pitch_num} overall score: {avg_score:.2f}/10")
            
            # Log key evaluation components
            logger.debug(f"Pitch {pitch_num} has {len(evaluation.get('key_strengths', []))} key strengths")
            logger.debug(f"Pitch {pitch_num} has {len(evaluation.get('areas_for_improvement', []))} areas for improvement")
            logger.superdebug(f"Full evaluation for pitch {pitch_num}: {evaluation}")
            
        logger.info(f"Successfully evaluated all {len(pitches)} pitches")
        self._log_method_end("evaluate_pitches", result=f"{len(evaluations)} evaluations")
        return evaluations

    def _format_pitch_for_evaluation(self, pitch: Dict[str, str]) -> str:
        """Format a pitch dictionary into a text string for evaluation.
        
        Args:
            pitch: Pitch dictionary with title, hook, premise, etc.
            
        Returns:
            Formatted pitch text
        """
        sections = []
        
        # Add title if available
        if "title" in pitch:
            sections.append(f"# {pitch['title']}")
        
        # Add other sections in a specific order
        for section_name, label in [
            ("hook", "## Hook"),
            ("premise", "## Premise"),
            ("main_conflict", "## Main Conflict"),
            ("unique_twist", "## Unique Twist")
        ]:
            if section_name in pitch:
                sections.append(f"{label}\n{pitch[section_name]}")
        
        # Join all sections with double newlines
        formatted_pitch = "\n\n".join(sections)
        return formatted_pitch

    def _parse_evaluation(self, response: str, pitch_num: int) -> Dict[str, Any]:
        """Parse the LLM evaluation response into a structured format.
        
        Args:
            response: Raw LLM response text
            pitch_num: Pitch number for logging
            
        Returns:
            Structured evaluation dictionary
        """
        logger.debug(f"Parsing evaluation response for pitch {pitch_num}")
        
        evaluation = {
            "scores": {},
            "key_strengths": [],
            "areas_for_improvement": []
        }
        
        # Track the current section being parsed
        current_section = None
        
        # Parse response line by line
        for i, line in enumerate(response.split('\n')):
            line = line.strip()
            if not line:
                continue
                
            logger.superdebug(f"Parsing evaluation line {i+1}: {line}")
            
            # Detect section headers
            if line.startswith('# Evaluation'):
                continue
            elif line.startswith('## Scores'):
                current_section = "scores"
                logger.debug(f"Found scores section for pitch {pitch_num}")
                continue
            elif line.startswith('## Key Strengths'):
                current_section = "strengths"
                logger.debug(f"Found key strengths section for pitch {pitch_num}")
                continue
            elif line.startswith('## Areas for Improvement'):
                current_section = "improvements"
                logger.debug(f"Found areas for improvement section for pitch {pitch_num}")
                continue
            elif line.startswith('##'):
                current_section = "other"
                continue
                
            # Parse content based on current section
            if current_section == "scores" and line.startswith('-'):
                # Parse score line (e.g., "- Originality: 8/10")
                score_match = re.match(r'-\s*([^:]+):\s*(\d+(?:\.\d+)?)/10', line)
                if score_match:
                    category = score_match.group(1).strip().lower().replace(' ', '_')
                    score = float(score_match.group(2))
                    evaluation["scores"][category] = score
                    logger.superdebug(f"Found score for pitch {pitch_num}: {category} = {score}")
                    
                    # Check for overall score, might be calculated average
                    if "overall" in category:
                        evaluation["overall_score"] = score
                        
            elif current_section == "strengths" and line.startswith('-'):
                # Parse strength point
                strength = line[1:].strip()
                if strength:
                    evaluation["key_strengths"].append(strength)
                    logger.superdebug(f"Found strength for pitch {pitch_num}: {strength[:50]}...")
                    
            elif current_section == "improvements" and line.startswith('-'):
                # Parse improvement point
                improvement = line[1:].strip()
                if improvement:
                    evaluation["areas_for_improvement"].append(improvement)
                    logger.superdebug(f"Found improvement for pitch {pitch_num}: {improvement[:50]}...")
        
        # Calculate overall score if not explicitly provided
        if "overall_score" not in evaluation and evaluation["scores"]:
            scores = evaluation["scores"]
            evaluation["overall_score"] = sum(scores.values()) / len(scores)
            logger.debug(f"Calculated overall score for pitch {pitch_num}: {evaluation['overall_score']:.2f}")
            
        # Check if we have the expected data
        if not evaluation["scores"]:
            logger.warning(f"No scores found in evaluation for pitch {pitch_num}")
            
        if not evaluation["key_strengths"]:
            logger.warning(f"No key strengths found in evaluation for pitch {pitch_num}")
            
        if not evaluation["areas_for_improvement"]:
            logger.warning(f"No areas for improvement found in evaluation for pitch {pitch_num}")
            
        # Log the parsed evaluation structure
        logger.debug(f"Successfully parsed evaluation for pitch {pitch_num}")
        logger.debug(f"Pitch {pitch_num} scores: {len(evaluation['scores'])} categories")
        logger.debug(f"Pitch {pitch_num} strengths: {len(evaluation['key_strengths'])} items")
        logger.debug(f"Pitch {pitch_num} improvements: {len(evaluation['areas_for_improvement'])} items")
        
        return evaluation 