"""Tropemaster Agent for analyzing and improving tropes in story pitches.

This agent identifies common tropes in a story pitch and suggests more original
alternatives or creative twists to enhance uniqueness and originality.
"""

import logging
import re
from typing import Dict, List, Any

from novel_writer.config.llm import LLMConfig
from novel_writer.agents.base_agent import BaseAgent

# Initialize logger
logger = logging.getLogger(__name__)

class TropemasterAgent(BaseAgent):
    """Agent responsible for identifying and improving tropes in story pitches.
    
    This agent analyzes story pitches to identify common or overused tropes,
    then suggests original alternatives or creative twists to enhance the
    uniqueness and originality of the story concept.
    """

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Tropemaster Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Tropemaster Agent")
        
    async def analyze_tropes(
        self, 
        pitch: Dict[str, str], 
        genre: str, 
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> Dict[str, Any]:
        """Analyze a story pitch for common tropes and suggest improvements.
        
        This method identifies common or overused tropes in the provided story
        pitch, then suggests unique alternatives or creative twists that maintain
        the core appeal while enhancing originality.
        
        Args:
            pitch: The story pitch to analyze
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes being explored
            
        Returns:
            Dictionary containing identified tropes and suggested alternatives
        """
        self._log_method_start(
            "analyze_tropes", 
            pitch_title=pitch.get("title", "Untitled"),
            genre=genre,
            subgenre=subgenre,
            themes_count=len(themes)
        )
        
        logger.info(f"Analyzing tropes in pitch: {pitch.get('title', 'Untitled')}")
        logger.debug(f"Genre: {genre}, Subgenre: {subgenre}")
        logger.debug(f"Tone: {tone[:50]}..." if len(tone) > 50 else f"Tone: {tone}")
        logger.debug(f"Themes: {', '.join(themes[:3])}" + (f"... and {len(themes)-3} more" if len(themes) > 3 else ""))
        
        # Format pitch components
        formatted_pitch = self._format_pitch(pitch)
        logger.debug(f"Formatted pitch for trope analysis, length: {len(formatted_pitch)} characters")
        
        # Format themes for the prompt
        themes_str = ", ".join(themes)
        
        # Construct the prompt for trope analysis
        prompt = f"""
You are a literary analyst specializing in trope identification and reinvention for {genre} stories.

Analyze this {subgenre} story pitch with a {tone} tone that explores these themes: {themes_str}.

{formatted_pitch}

First, identify 3-5 common or potentially overused tropes in this pitch. For each trope:
1. Name the trope
2. Explain how it appears in this pitch
3. Assess the level of overuse in {subgenre} stories (High/Medium/Low)

Then, for each identified trope, suggest 1-2 original alternatives or creative twists that would:
- Maintain the core appeal of the original trope
- Enhance the uniqueness of the story
- Better support the {tone} tone
- More effectively explore the themes
- Fit well within the {subgenre} subgenre

Format your response exactly as follows:

# Trope Analysis

## Identified Tropes
1. [TROPE NAME]: [Brief explanation of how it appears in the pitch] | Overuse Level: [High/Medium/Low]
2. [TROPE NAME]: [Brief explanation of how it appears in the pitch] | Overuse Level: [High/Medium/Low]
3. [TROPE NAME]: [Brief explanation of how it appears in the pitch] | Overuse Level: [High/Medium/Low]
[and so on...]

## Suggested Alternatives

### For [TROPE 1]
- [Alternative 1]: [Explanation of how this alternative maintains appeal while being more original]
- [Alternative 2]: [Explanation of how this alternative maintains appeal while being more original]

### For [TROPE 2]
- [Alternative 1]: [Explanation of how this alternative maintains appeal while being more original]
- [Alternative 2]: [Explanation of how this alternative maintains appeal while being more original]

[and so on for each identified trope]

## Summary
[A brief paragraph summarizing how these improvements would enhance the story's originality while maintaining its core appeal]
"""
        logger.debug("Sending trope analysis prompt to LLM")
        logger.superdebug(f"Full trope analysis prompt:\n{prompt}")
        
        # Get response from LLM
        response = await self._get_llm_response(prompt)
        logger.info("Received trope analysis response from LLM")
        logger.superdebug(f"Raw trope analysis response length: {len(response)} characters")
        
        # Parse the analysis response
        analysis = self._parse_trope_analysis(response)
        
        # Log the results
        if "identified_tropes" in analysis:
            trope_count = len(analysis["identified_tropes"])
            logger.info(f"Identified {trope_count} tropes in the pitch")
            
            # Log overuse levels
            high_overuse = sum(1 for t in analysis["identified_tropes"] if t.get("overuse_level", "").lower() == "high")
            medium_overuse = sum(1 for t in analysis["identified_tropes"] if t.get("overuse_level", "").lower() == "medium")
            low_overuse = sum(1 for t in analysis["identified_tropes"] if t.get("overuse_level", "").lower() == "low")
            
            logger.debug(f"Overuse levels: {high_overuse} high, {medium_overuse} medium, {low_overuse} low")
            
            # Log a few sample tropes
            for i, trope in enumerate(analysis["identified_tropes"][:2], 1):
                logger.debug(f"Trope {i}: {trope.get('name', 'Unnamed')} - {trope.get('explanation', '')[:50]}...")
            if trope_count > 2:
                logger.debug(f"...and {trope_count - 2} more tropes")
        
        if "suggested_alternatives" in analysis:
            alternative_count = sum(len(alts) for alts in analysis["suggested_alternatives"].values())
            logger.info(f"Generated {alternative_count} alternative suggestions")
            
            # Log a sample of alternatives
            trope_names = list(analysis["suggested_alternatives"].keys())
            if trope_names:
                sample_trope = trope_names[0]
                sample_alts = analysis["suggested_alternatives"][sample_trope]
                logger.debug(f"For trope '{sample_trope}': {len(sample_alts)} alternatives")
                if sample_alts:
                    logger.debug(f"Example alternative: {sample_alts[0].get('description', '')[:50]}...")
        
        if "summary" in analysis:
            logger.debug(f"Analysis summary length: {len(analysis['summary'])} characters")
            
        self._log_method_end("analyze_tropes", result=f"{len(analysis.get('identified_tropes', []))} tropes analyzed")
        return analysis
        
    def _format_pitch(self, pitch: Dict[str, str]) -> str:
        """Format the pitch for trope analysis.
        
        Args:
            pitch: Dictionary containing pitch components
            
        Returns:
            Formatted pitch string
        """
        logger.debug("Formatting pitch for trope analysis")
        logger.superdebug(f"Pitch components: {list(pitch.keys())}")
        
        formatted_sections = [
            f"# Story Pitch: {pitch.get('title', 'Untitled')}",
            "",
            "## Hook",
            f"{pitch.get('hook', 'No hook provided')}",
            "",
            "## Premise",
            f"{pitch.get('premise', 'No premise provided')}",
            "",
            "## Main Conflict",
            f"{pitch.get('main_conflict', 'No main conflict provided')}",
            "",
            "## Unique Twist",
            f"{pitch.get('unique_twist', 'No unique twist provided')}"
        ]
        
        # Add additional components if available
        if "characters" in pitch and pitch["characters"]:
            formatted_sections.extend([
                "",
                "## Characters",
                f"{pitch['characters']}"
            ])
            
        if "setting" in pitch and pitch["setting"]:
            formatted_sections.extend([
                "",
                "## Setting",
                f"{pitch['setting']}"
            ])
            
        formatted_pitch = "\n".join(formatted_sections)
        logger.superdebug(f"Formatted pitch:\n{formatted_pitch}")
        return formatted_pitch
        
    def _parse_trope_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the LLM trope analysis response into a structured format.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Structured analysis dictionary
        """
        logger.debug("Parsing trope analysis response")
        
        analysis = {
            "identified_tropes": [],
            "suggested_alternatives": {},
            "summary": ""
        }
        
        current_section = None
        current_trope = None
        
        # Regex patterns for parsing
        trope_pattern = re.compile(r'^\d+\.\s+(.+?):\s+(.+?)\s*\|\s*Overuse Level:\s*(\w+)')
        alternative_pattern = re.compile(r'^-\s+(.+?):\s+(.+)')
        
        # Parse the response line by line
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            logger.superdebug(f"Parsing line: {line[:50]}..." if len(line) > 50 else f"Parsing line: {line}")
            
            # Check for section headers
            if line.startswith('## Identified Tropes'):
                current_section = 'tropes'
                logger.debug("Found identified tropes section")
                continue
            elif line.startswith('## Suggested Alternatives'):
                current_section = 'alternatives'
                logger.debug("Found suggested alternatives section")
                continue
            elif line.startswith('## Summary'):
                current_section = 'summary'
                logger.debug("Found summary section")
                continue
            elif line.startswith('# '):
                # Main section header, ignore
                continue
                
            # Process content based on current section
            if current_section == 'tropes':
                # Try to match trope pattern
                match = trope_pattern.search(line)
                if match:
                    name, explanation, overuse_level = match.groups()
                    trope = {
                        "name": name.strip(),
                        "explanation": explanation.strip(),
                        "overuse_level": overuse_level.strip()
                    }
                    analysis["identified_tropes"].append(trope)
                    logger.debug(f"Found trope: {name.strip()} (Overuse: {overuse_level.strip()})")
                    
            elif current_section == 'alternatives':
                # Check for "### For [TROPE]" header
                if line.startswith('### For '):
                    current_trope = line[8:].strip()
                    if current_trope not in analysis["suggested_alternatives"]:
                        analysis["suggested_alternatives"][current_trope] = []
                    logger.debug(f"Processing alternatives for trope: {current_trope}")
                # Check for alternative entries
                elif current_trope and line.startswith('-'):
                    match = alternative_pattern.search(line)
                    if match:
                        alt_name, alt_description = match.groups()
                        alternative = {
                            "name": alt_name.strip(),
                            "description": alt_description.strip()
                        }
                        analysis["suggested_alternatives"][current_trope].append(alternative)
                        logger.superdebug(f"Found alternative: {alt_name.strip()}")
                    
            elif current_section == 'summary':
                # Collect all lines as part of the summary
                if analysis["summary"]:
                    analysis["summary"] += " " + line
                else:
                    analysis["summary"] = line
                    
        # Clean up the summary
        if analysis["summary"]:
            analysis["summary"] = analysis["summary"].strip()
            logger.debug("Parsed summary")
            
        # Log the parsing results
        logger.debug(f"Parsed analysis with:")
        logger.debug(f"- {len(analysis['identified_tropes'])} identified tropes")
        logger.debug(f"- {len(analysis['suggested_alternatives'])} tropes with alternatives")
        total_alternatives = sum(len(alts) for alts in analysis['suggested_alternatives'].values())
        logger.debug(f"- {total_alternatives} total alternative suggestions")
        
        return analysis 