"""Improver Agent for enhancing story pitches.

This agent is responsible for taking evaluated story pitches and improving
them based on the feedback provided by the Critic Agent. It enhances the
original pitches while preserving their core strengths.
"""

import logging
import re
from typing import Dict, List, Any

from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.agents.base_agent import BaseAgent

# Initialize logger
logger = logging.getLogger(__name__)

class ImproverAgent(BaseAgent):
    """Agent responsible for improving story pitches.
    
    This agent analyzes pitches and their evaluations to produce enhanced
    versions that address weaknesses while preserving core strengths.
    It helps to refine promising story concepts into their best possible form.
    """

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
    ) -> Dict[str, str]:
        """Improve a story pitch based on evaluation feedback.
        
        Takes an original pitch and its evaluation, then generates an
        improved version that addresses the weaknesses while preserving
        the strengths.
        
        Args:
            pitch: The original story pitch
            evaluation: Evaluation data for the pitch
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            Improved story pitch dictionary
        """
        self._log_method_start(
            "improve_pitch", 
            pitch_title=pitch.get("title", "Untitled"),
            genre=genre,
            subgenre=subgenre,
            themes_count=len(themes)
        )
        
        logger.info(f"Improving pitch: {pitch.get('title', 'Untitled')}")
        logger.debug(f"Original pitch has {len(pitch)} components")
        logger.superdebug(f"Original pitch details: {pitch}")
        
        # Format the evaluation data for the prompt
        if "scores" in evaluation:
            avg_score = sum(evaluation["scores"].values()) / len(evaluation["scores"])
            logger.debug(f"Pitch evaluation score: {avg_score:.2f}/10")
            
        # Format themes for the prompt
        themes_str = ", ".join(themes)
        logger.debug(f"Using {len(themes)} themes: {themes_str}")
        
        # Prepare key strengths and areas for improvement
        key_strengths = evaluation.get("key_strengths", [])
        areas_for_improvement = evaluation.get("areas_for_improvement", [])
        
        logger.debug(f"Pitch has {len(key_strengths)} key strengths")
        logger.debug(f"Pitch has {len(areas_for_improvement)} areas for improvement")
        
        # Format original pitch components
        original_pitch_text = self._format_pitch_for_prompt(pitch)
        logger.debug(f"Formatted original pitch text, length: {len(original_pitch_text)} characters")
        logger.superdebug(f"Original pitch text:\n{original_pitch_text}")
        
        # Format evaluation components
        strengths_text = "\n".join(f"- {strength}" for strength in key_strengths)
        improvements_text = "\n".join(f"- {improvement}" for improvement in areas_for_improvement)
        
        # Construct the prompt
        prompt = f"""
Improve this {subgenre} story pitch based on the evaluation feedback. 
The story should maintain a {tone} tone and explore these themes: {themes_str}.

# ORIGINAL PITCH
{original_pitch_text}

# EVALUATION FEEDBACK
## Key Strengths (preserve these)
{strengths_text}

## Areas for Improvement (address these)
{improvements_text}

Create an improved version of this pitch. Keep the core concept and strengths, but address the weaknesses.
Include all five components: title, hook, premise, main conflict, and unique twist.

Format your response as follows:

# Improved Pitch
## Title
[Improved title]

## Hook
[Improved one-sentence hook]

## Premise
[Improved premise]

## Main Conflict
[Improved main conflict]

## Unique Twist
[Improved unique twist]

## Improvements Made
[List the specific improvements made and how they address the feedback]

## Elements Preserved
[List the key strengths and elements that were preserved from the original]
"""
        logger.debug("Sending improvement prompt to LLM")
        logger.superdebug(f"Full improvement prompt:\n{prompt}")
        
        # Get response from LLM
        response = await self._get_llm_response(prompt)
        logger.info("Received improvement response from LLM")
        logger.superdebug(f"Raw improvement response length: {len(response)} characters")
        
        # Parse the improved pitch
        improved_pitch = self._parse_improved_pitch(response)
        
        if improved_pitch:
            logger.info(f"Successfully improved pitch: {improved_pitch.get('title', 'Untitled')}")
            logger.debug(f"Improved pitch has {len(improved_pitch)} components")
            logger.superdebug(f"Improved pitch details: {improved_pitch}")
            
            # Compare with original and log the differences
            if "title" in pitch and "title" in improved_pitch and pitch["title"] != improved_pitch["title"]:
                logger.debug(f"Title changed from '{pitch['title']}' to '{improved_pitch['title']}'")
                
            # Log improvements made section if available
            if "improvements_made" in improved_pitch:
                improvements = improved_pitch["improvements_made"]
                if isinstance(improvements, list):
                    logger.debug(f"Improver made {len(improvements)} specific improvements")
                    for i, improvement in enumerate(improvements[:2], 1):
                        logger.debug(f"Improvement {i}: {improvement[:80]}...")
                    if len(improvements) > 2:
                        logger.debug(f"...and {len(improvements) - 2} more improvements")
            
            self._log_method_end("improve_pitch", result=improved_pitch.get("title", "Untitled"))
            return improved_pitch
        else:
            error_msg = "Failed to parse improved pitch from LLM response"
            logger.error(error_msg)
            self._log_method_error("improve_pitch", ValueError(error_msg))
            # Return the original pitch if parsing fails
            logger.warning("Returning original pitch due to parsing failure")
            return pitch

    def _format_pitch_for_prompt(self, pitch: Dict[str, str]) -> str:
        """Format a pitch dictionary into a text string for the prompt.
        
        Args:
            pitch: Pitch dictionary with title, hook, premise, etc.
            
        Returns:
            Formatted pitch text
        """
        sections = []
        
        # Add title if available
        if "title" in pitch:
            sections.append(f"## Title\n{pitch['title']}")
        
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

    def _parse_improved_pitch(self, response: str) -> Dict[str, Any]:
        """Parse the LLM improved pitch response into a structured format.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Structured improved pitch dictionary
        """
        logger.debug("Parsing improved pitch from LLM response")
        
        improved_pitch = {}
        current_section = None
        section_content = []
        improvements_made = []
        elements_preserved = []
        
        # Define section mappings for standardization
        section_mappings = {
            "title": "title",
            "hook": "hook",
            "premise": "premise",
            "main conflict": "main_conflict",
            "unique twist": "unique_twist",
            "improvements made": "improvements_made",
            "elements preserved": "elements_preserved"
        }
        
        # Parse response line by line
        for i, line in enumerate(response.split('\n')):
            line = line.strip()
            if not line:
                continue
                
            logger.superdebug(f"Parsing line {i+1}: {line}")
            
            # Check for section headers (## Section)
            if line.startswith('## '):
                # If we were collecting content for a previous section, save it
                if current_section and section_content:
                    section_text = ' '.join(section_content)
                    
                    # Handle special sections
                    if current_section == "improvements_made":
                        # Extract list items if present
                        items = [item.strip()[2:].strip() for item in section_content if item.strip().startswith('- ')]
                        if items:
                            improvements_made = items
                        else:
                            improvements_made = [section_text]
                    elif current_section == "elements_preserved":
                        # Extract list items if present
                        items = [item.strip()[2:].strip() for item in section_content if item.strip().startswith('- ')]
                        if items:
                            elements_preserved = items
                        else:
                            elements_preserved = [section_text]
                    else:
                        # Regular pitch section
                        improved_pitch[current_section] = section_text
                
                # Start new section
                section_header = line[3:].lower()
                current_section = section_mappings.get(section_header, section_header)
                logger.debug(f"Found section: {current_section}")
                section_content = []
                
            # Check for major headers (# Section)    
            elif line.startswith('# '):
                # Skip these headers
                continue
                
            # Process list items in special sections    
            elif current_section in ["improvements_made", "elements_preserved"] and line.startswith('- '):
                section_content.append(line)
                logger.superdebug(f"Added list item to {current_section}: {line}")
                
            # Add content to the current section
            elif current_section:
                section_content.append(line)
                logger.superdebug(f"Added line to {current_section}: {line[:30]}...")
        
        # Handle any remaining section
        if current_section and section_content:
            section_text = ' '.join(section_content)
            
            if current_section == "improvements_made":
                items = [item.strip()[2:].strip() for item in section_content if item.strip().startswith('- ')]
                if items:
                    improvements_made = items
                else:
                    improvements_made = [section_text]
            elif current_section == "elements_preserved":
                items = [item.strip()[2:].strip() for item in section_content if item.strip().startswith('- ')]
                if items:
                    elements_preserved = items
                else:
                    elements_preserved = [section_text]
            else:
                improved_pitch[current_section] = section_text
        
        # Add improvements and elements lists
        if improvements_made:
            improved_pitch["improvements_made"] = improvements_made
            logger.debug(f"Extracted {len(improvements_made)} improvements made")
            
        if elements_preserved:
            improved_pitch["elements_preserved"] = elements_preserved
            logger.debug(f"Extracted {len(elements_preserved)} elements preserved")
        
        # Validate that we have the required fields
        required_fields = ["title", "hook", "premise", "main_conflict", "unique_twist"]
        missing_fields = [field for field in required_fields if field not in improved_pitch]
        
        if missing_fields:
            logger.warning(f"Improved pitch is missing required fields: {missing_fields}")
            for field in missing_fields:
                improved_pitch[field] = "[Missing]"
                logger.debug(f"Added placeholder for missing field: {field}")
            
        logger.debug(f"Successfully parsed improved pitch with {len(improved_pitch)} components")
        return improved_pitch

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