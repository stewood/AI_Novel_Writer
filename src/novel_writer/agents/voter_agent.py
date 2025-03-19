"""Voter Agent for selecting the best story pitch.

This agent is responsible for analyzing multiple story pitches and their
evaluations to determine the most promising concept to develop further.
"""

import logging
import re
from typing import Dict, List, Any

from novel_writer.config.llm import LLMConfig
from novel_writer.agents.base_agent import BaseAgent

# Initialize logger
logger = logging.getLogger(__name__)

class VoterAgent(BaseAgent):
    """Agent responsible for selecting the best story pitch.
    
    This agent analyzes multiple story pitches and their evaluations to
    determine which concept is most promising. It provides a decision
    with clear rationale, development recommendations, and notes on
    potential challenges.
    """

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Voter Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Voter Agent")

    def _format_pitches_and_evaluations(
        self,
        pitches: List[Dict[str, str]],
        evaluations: List[Dict[str, Any]]
    ) -> str:
        """Format the pitches and evaluations for the selection prompt.
        
        Args:
            pitches: List of story pitches
            evaluations: List of pitch evaluations
            
        Returns:
            Formatted text with numbered pitches and their evaluations
        """
        logger.debug("Formatting pitches and evaluations for selection")
        
        formatted_text = []
        
        for i, (pitch, evaluation) in enumerate(zip(pitches, evaluations), 1):
            pitch_title = pitch.get("title", f"Untitled Pitch {i}")
            logger.debug(f"Formatting pitch {i}: {pitch_title}")
            logger.superdebug(f"Full pitch {i} details: {pitch}")
            logger.superdebug(f"Full evaluation {i} details: {evaluation}")
            
            # Calculate average score
            avg_score = 0
            if "overall_score" in evaluation:
                avg_score = evaluation["overall_score"]
                logger.debug(f"Using overall score for pitch {i}: {avg_score}")
            elif "scores" in evaluation and evaluation["scores"]:
                scores = evaluation["scores"]
                avg_score = sum(scores.values()) / len(scores)
                logger.debug(f"Calculated average score for pitch {i}: {avg_score:.2f}")
                
            # Format the pitch and evaluation
            pitch_section = [
                f"# Pitch {i}: {pitch_title}",
                f"## Score: {avg_score:.1f}/10",
                "",
                f"## Hook",
                f"{pitch.get('hook', 'No hook provided')}",
                "",
                f"## Premise",
                f"{pitch.get('premise', 'No premise provided')}",
                "",
                f"## Main Conflict",
                f"{pitch.get('main_conflict', 'No main conflict provided')}",
                "",
                f"## Unique Twist",
                f"{pitch.get('unique_twist', 'No unique twist provided')}",
                "",
                "## Key Strengths",
            ]
            
            # Add strengths
            for strength in evaluation.get("key_strengths", []):
                pitch_section.append(f"- {strength}")
                
            pitch_section.append("")
            pitch_section.append("## Areas for Improvement")
            
            # Add areas for improvement
            for area in evaluation.get("areas_for_improvement", []):
                pitch_section.append(f"- {area}")
                
            formatted_text.append("\n".join(pitch_section))
            logger.debug(f"Completed formatting for pitch {i}")
            
        return "\n\n" + "\n\n".join(formatted_text)

    async def select_best_pitch(
        self,
        pitches: List[Dict[str, str]],
        evaluations: List[Dict[str, Any]],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> Dict[str, Any]:
        """Select the best pitch from multiple options.
        
        Analyzes the pitches and evaluations to determine which concept
        is most promising for further development.
        
        Args:
            pitches: List of story pitches
            evaluations: List of pitch evaluations
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            Dictionary with selection results including winner and rationale
        """
        self._log_method_start(
            "select_best_pitch", 
            pitches_count=len(pitches),
            genre=genre,
            subgenre=subgenre,
            themes_count=len(themes)
        )
        
        logger.info(f"Selecting best pitch from {len(pitches)} options for {subgenre} story")
        logger.debug(f"Using tone: {tone[:50]}..." if len(tone) > 50 else f"Using tone: {tone}")
        logger.debug(f"Using {len(themes)} themes")
        
        # Format pitches and evaluations
        formatted_content = self._format_pitches_and_evaluations(pitches, evaluations)
        logger.debug(f"Formatted content for selection, length: {len(formatted_content)} characters")
        
        # Format themes for the prompt
        themes_str = ", ".join(themes)
        
        # Construct the prompt
        prompt = f"""
You are a literary agent tasked with selecting the most promising story pitch for a {subgenre} story in the {genre} genre.
The story should have a {tone} tone and explore these themes: {themes_str}.

Below are {len(pitches)} pitches with their evaluations. Select the BEST pitch to develop into a full story.

{formatted_content}

Make your selection based on:
1. Overall quality and potential
2. Fit with the {subgenre} genre and specified themes
3. Commercial viability and audience appeal
4. Uniqueness and originality
5. Emotional resonance and depth

Return your selection in this format:

# Selection
## Winner
[Title of the winning pitch]

## Selection Criteria
- [Specific reason this pitch was selected over others]
- [Specific reason this pitch was selected over others]
- [Specific reason this pitch was selected over others]

## Development Recommendations
- [Recommendation for developing this pitch further]
- [Recommendation for developing this pitch further]
- [Recommendation for developing this pitch further]

## Potential Challenges
- [Potential challenge or obstacle to be aware of]
- [Potential challenge or obstacle to be aware of]
- [Potential challenge or obstacle to be aware of]

Be objective and consider both artistic merit and commercial potential in your selection.
"""
        logger.debug("Sending selection prompt to LLM")
        logger.superdebug(f"Full selection prompt:\n{prompt}")
        
        # Get response from LLM
        response = await self._get_llm_response(prompt)
        logger.info("Received selection response from LLM")
        logger.superdebug(f"Raw selection response length: {len(response)} characters")
        
        # Parse the selection response
        selection = self._parse_selection(response)
        
        if "winner" in selection:
            winner = selection["winner"]
            logger.info(f"Selected winner: {winner}")
            
            # Log other selection components
            if "selection_criteria" in selection:
                logger.debug(f"Selection based on {len(selection['selection_criteria'])} criteria")
                for i, criterion in enumerate(selection['selection_criteria'][:2], 1):
                    logger.debug(f"Criterion {i}: {criterion[:80]}...")
                if len(selection['selection_criteria']) > 2:
                    logger.debug(f"...and {len(selection['selection_criteria']) - 2} more criteria")
                    
            if "development_recommendations" in selection:
                logger.debug(f"Provided {len(selection['development_recommendations'])} development recommendations")
                
            if "potential_challenges" in selection:
                logger.debug(f"Identified {len(selection['potential_challenges'])} potential challenges")
                
            self._log_method_end("select_best_pitch", result=winner)
            return selection
        else:
            error_msg = "No winner selected in LLM response"
            logger.error(error_msg)
            self._log_method_error("select_best_pitch", ValueError(error_msg))
            
            # Fall back to highest scored pitch
            fallback_winner = self._select_fallback_winner(pitches, evaluations)
            logger.warning(f"Using fallback selection: {fallback_winner}")
            
            return {
                "winner": fallback_winner,
                "selection_criteria": ["Selected based on highest evaluation score (fallback method)"],
                "development_recommendations": [],
                "potential_challenges": []
            }

    def _parse_selection(self, response: str) -> Dict[str, Any]:
        """Parse the LLM selection response into a structured format.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Structured selection dictionary
        """
        logger.debug("Parsing selection response from LLM")
        
        selection = {
            "selection_criteria": [],
            "development_recommendations": [],
            "potential_challenges": []
        }
        
        current_section = None
        
        # Parse response line by line
        for i, line in enumerate(response.split('\n')):
            line = line.strip()
            if not line:
                continue
                
            logger.superdebug(f"Parsing line {i+1}: {line}")
            
            # Check for section headers
            if line.startswith('## Winner'):
                current_section = "winner"
                logger.debug("Found winner section")
                continue
            elif line.startswith('## Selection Criteria'):
                current_section = "criteria"
                logger.debug("Found selection criteria section")
                continue
            elif line.startswith('## Development Recommendations'):
                current_section = "recommendations"
                logger.debug("Found development recommendations section")
                continue
            elif line.startswith('## Potential Challenges'):
                current_section = "challenges"
                logger.debug("Found potential challenges section")
                continue
            elif line.startswith('#'):
                current_section = None
                continue
                
            # Parse content based on current section
            if current_section == "winner":
                # The winner should be just the title line after "## Winner"
                selection["winner"] = line
                logger.debug(f"Found winner: {line}")
            elif current_section == "criteria" and line.startswith('-'):
                criterion = line[1:].strip()
                selection["selection_criteria"].append(criterion)
                logger.superdebug(f"Found selection criterion: {criterion}")
            elif current_section == "recommendations" and line.startswith('-'):
                recommendation = line[1:].strip()
                selection["development_recommendations"].append(recommendation)
                logger.superdebug(f"Found development recommendation: {recommendation}")
            elif current_section == "challenges" and line.startswith('-'):
                challenge = line[1:].strip()
                selection["potential_challenges"].append(challenge)
                logger.superdebug(f"Found potential challenge: {challenge}")
                
        # Check if we have at least the winner
        if "winner" not in selection or not selection["winner"]:
            logger.warning("No winner found in selection response")
            
        # Log the parsing results
        logger.debug(f"Parsed selection with:")
        if "winner" in selection:
            logger.debug(f"- Winner: {selection['winner']}")
        logger.debug(f"- {len(selection['selection_criteria'])} selection criteria")
        logger.debug(f"- {len(selection['development_recommendations'])} development recommendations")
        logger.debug(f"- {len(selection['potential_challenges'])} potential challenges")
            
        return selection
        
    def _select_fallback_winner(
        self,
        pitches: List[Dict[str, str]],
        evaluations: List[Dict[str, Any]]
    ) -> str:
        """Select a fallback winner based on highest score.
        
        Args:
            pitches: List of story pitches
            evaluations: List of pitch evaluations
            
        Returns:
            Title of the highest-scoring pitch
        """
        logger.debug("Selecting fallback winner based on highest score")
        
        # Find the highest-scoring pitch
        highest_score = -1
        highest_index = 0
        
        for i, evaluation in enumerate(evaluations):
            score = 0
            if "overall_score" in evaluation:
                score = evaluation["overall_score"]
            elif "scores" in evaluation and evaluation["scores"]:
                score = sum(evaluation["scores"].values()) / len(evaluation["scores"])
                
            logger.debug(f"Pitch {i+1} score: {score}")
            
            if score > highest_score:
                highest_score = score
                highest_index = i
                logger.debug(f"New highest score: {score} (pitch {i+1})")
                
        # Get the title of the highest-scoring pitch
        winner_title = pitches[highest_index].get("title", f"Pitch {highest_index + 1}")
        logger.debug(f"Selected fallback winner: {winner_title} with score {highest_score}")
        
        return winner_title 