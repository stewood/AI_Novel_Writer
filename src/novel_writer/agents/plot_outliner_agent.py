"""Agent responsible for generating a structured 24-chapter novel outline.

This agent takes a story idea and generates a detailed 24-chapter outline following
a three-act structure. It ensures proper pacing, character development, and
theme integration throughout the story arc.
"""

import logging
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

from novel_writer.config.llm import LLMConfig

logger = logging.getLogger(__name__)

class PlotOutlinerAgent:
    """Agent that generates a detailed 24-chapter novel outline.
    
    This agent creates a comprehensive story outline that includes:
    - Three-act structure (Act I: Setup, Act II: Confrontation, Act III: Resolution)
    - 24 chapters with detailed events and character focus
    - Emotional character arcs and theme integration
    - Proper pacing and tension building
    
    The outline follows standard novel structure while incorporating the specific
    genre, tone, and themes of the story.
    """
    
    def __init__(self, llm_config: LLMConfig):
        """Initialize the PlotOutlinerAgent.
        
        Args:
            llm_config: Configuration for the language model
        """
        self.llm_config = llm_config
        logger.debug("PlotOutlinerAgent initialized")
        
    async def generate_outline(
        self,
        title: str,
        genre: str,
        tone: str,
        themes: List[str],
        summary: str
    ) -> Dict[str, Any]:
        """Generate a complete 24-chapter outline.
        
        This method creates a detailed outline following a three-act structure:
        - Act I (Chapters 1-6): Setup and inciting incident
        - Act IIa (Chapters 7-12): Rising action and complications
        - Act IIb (Chapters 13-18): Midpoint and escalating conflict
        - Act III (Chapters 19-24): Climax and resolution
        
        Each chapter includes:
        - Title and act designation
        - Key events and plot points
        - Character emotional development
        - Character focus and interactions
        - Chapter summary
        
        Args:
            title: Story title
            genre: Story genre (e.g., "Science Fiction", "Fantasy")
            tone: Narrative tone (e.g., "Optimistic", "Dark")
            themes: List of core themes to incorporate
            summary: Original story summary to expand upon
            
        Returns:
            Dictionary containing the complete outline data with structure:
            {
                "metadata": {
                    "title": str,
                    "genre": str,
                    "tone": str,
                    "themes": List[str],
                    "summary": str
                },
                "chapters": [
                    {
                        "chapter_number": int,
                        "chapter_title": str,
                        "act": str,
                        "key_events": List[str],
                        "emotional_turn": str,
                        "character_focus": List[str],
                        "chapter_summary": str
                    },
                    ...
                ]
            }
            
        Raises:
            Exception: If outline generation fails
        """
        logger.info("Starting outline generation")
        logger.debug(f"Input - Title: {title}, Genre: {genre}")
        logger.debug(f"Themes: {themes}")
        
        # Define the act structure
        acts = {
            "I": {
                "name": "Setup",
                "chapters": range(1, 7),
                "goals": [
                    "Introduce protagonist and setting",
                    "Disrupt the status quo",
                    "Explore emotional resistance",
                    "Attempt to fix the problem and fail",
                    "Force a meaningful choice"
                ]
            },
            "IIa": {
                "name": "Rising Action",
                "chapters": range(7, 13),
                "goals": [
                    "New world, allies, and skills",
                    "Small victories with growing threats",
                    "Growing emotional investment",
                    "Rising stakes and false hope"
                ]
            },
            "IIb": {
                "name": "Collapse",
                "chapters": range(13, 19),
                "goals": [
                    "Major failures and consequences",
                    "Emotional fallout and isolation",
                    "Mistakes and their price",
                    "Rock bottom moment"
                ]
            },
            "III": {
                "name": "Resolution",
                "chapters": range(19, 25),
                "goals": [
                    "Rebuild and recommit",
                    "Face the antagonist",
                    "Make a final revelation",
                    "Succeed or fail with emotional closure"
                ]
            }
        }
        
        # Generate chapters for each act
        chapters = []
        
        for act_id, act_info in acts.items():
            logger.info(f"Generating chapters for Act {act_id}")
            
            act_chapters = await self._generate_act_chapters(
                act_id=act_id,
                act_name=act_info["name"],
                chapter_range=act_info["chapters"],
                act_goals=act_info["goals"],
                title=title,
                genre=genre,
                tone=tone,
                themes=themes,
                summary=summary
            )
            
            chapters.extend(act_chapters)
            logger.debug(f"Generated {len(act_chapters)} chapters for Act {act_id}")
        
        logger.info("Completed outline generation")
        logger.debug(f"Generated {len(chapters)} total chapters")
        
        return {
            "status": "success",
            "chapters": chapters,
            "metadata": {
                "title": title,
                "genre": genre,
                "tone": tone,
                "themes": themes,
                "acts": acts
            }
        }
    
    async def _generate_chapter_prompt(
        self,
        act_id: str,
        act_name: str,
        act_goals: List[str],
        chapter_range: range,
        title: str,
        genre: str,
        tone: str,
        themes: List[str],
        summary: str
    ) -> str:
        """Generate the prompt for chapter generation.
        
        Args:
            act_id: Act identifier (I, IIa, IIb, III)
            act_name: Name of the act
            act_goals: List of narrative goals for this act
            chapter_range: Range of chapter numbers in this act
            title: Story title
            genre: Story genre
            tone: Narrative tone
            themes: List of themes
            summary: Original story summary
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert story outliner tasked with generating detailed chapter outlines for a novel.

STORY CONTEXT
Title: {title}
Genre: {genre}
Tone: {tone}
Themes: {', '.join(themes)}
Summary: {summary}

CURRENT ACT
Act {act_id}: {act_name}
Chapters: {chapter_range.start} to {chapter_range.stop - 1}
Act Goals:
{chr(10).join(f'- {goal}' for goal in act_goals)}

TASK
Generate detailed outlines for chapters {chapter_range.start} to {chapter_range.stop - 1} that fulfill the act's goals while maintaining narrative tension and character development.

For each chapter, provide:
1. A compelling chapter title that reflects the content
2. 2-4 key events that drive the story forward
3. The emotional turn (how characters change emotionally)
4. Which characters are the focus
5. A detailed one-paragraph summary

FORMAT
Return the chapters in Markdown format using this structure for each chapter:

## Chapter [Number]: [Title]

**Act:** [Act Number]

**Key Events:**
- [Event 1]
- [Event 2]
- [Event 3]

**Emotional Turn:** [How characters change emotionally]

**Character Focus:** [Main character(s) of the chapter]

**Summary:** [One paragraph chapter summary]

---

REQUIREMENTS
- Ensure each chapter builds on previous events
- Focus on character development and emotional arcs
- Maintain the specified tone throughout
- Incorporate the themes naturally
- Build tension appropriately for the act's position in the story
- Make each chapter title unique and evocative
- Keep summaries focused and impactful

Begin generating the chapter outlines now."""

        return prompt
        
    async def _generate_act_chapters(
        self,
        act_id: str,
        act_name: str,
        chapter_range: range,
        act_goals: List[str],
        title: str,
        genre: str,
        tone: str,
        themes: List[str],
        summary: str
    ) -> List[Dict[str, Any]]:
        """Generate chapters for a specific act.
        
        Args:
            act_id: Act identifier (I, IIa, IIb, III)
            act_name: Name of the act
            chapter_range: Range of chapter numbers in this act
            act_goals: List of narrative goals for this act
            title: Story title
            genre: Story genre
            tone: Narrative tone
            themes: List of themes
            summary: Original story summary
            
        Returns:
            List of chapter dictionaries
        """
        logger.debug(f"Generating chapters for Act {act_id}: {act_name}")
        
        # Generate the prompt
        prompt = await self._generate_chapter_prompt(
            act_id=act_id,
            act_name=act_name,
            act_goals=act_goals,
            chapter_range=chapter_range,
            title=title,
            genre=genre,
            tone=tone,
            themes=themes,
            summary=summary
        )
        
        logger.superdebug(f"Generated prompt for Act {act_id}:\n{prompt}")
        
        try:
            # Call the LLM to generate chapters
            response = await self.llm_config.generate_text(
                prompt=prompt,
                max_tokens=2000,  # Adjust based on needs
                temperature=0.7    # Balance creativity and consistency
            )
            
            logger.superdebug(f"Raw LLM response for Act {act_id}:\n{response}")
            
            # Parse the Markdown response into chapter dictionaries
            chapters_data = []
            current_chapter = {}
            
            for line in response.split('\n'):
                line = line.strip()
                
                # Skip empty lines and section separators
                if not line or line == '---':
                    continue
                    
                # Start a new chapter
                if line.startswith('## Chapter'):
                    # Save the previous chapter if it's complete
                    if current_chapter and all(field in current_chapter for field in [
                        "chapter_number", "chapter_title", "act",
                        "key_events", "emotional_turn", "character_focus",
                        "chapter_summary"
                    ]):
                        chapters_data.append(current_chapter)
                    
                    # Start a new chapter
                    try:
                        chapter_num = int(line.split(':')[0].split()[-1])
                        chapter_title = line.split(':')[1].strip()
                        current_chapter = {
                            "chapter_number": chapter_num,
                            "chapter_title": chapter_title,
                            "act": act_id,
                            "key_events": []  # Initialize empty list for key events
                        }
                    except (IndexError, ValueError) as e:
                        logger.error(f"Error parsing chapter header: {line}")
                        continue
                
                # Parse chapter content
                elif line.startswith('**Key Events:**'):
                    current_chapter["key_events"] = []
                elif line.startswith('- ') and "key_events" in current_chapter:
                    current_chapter["key_events"].append(line[2:])
                elif line.startswith('**Emotional Turn:**'):
                    current_chapter["emotional_turn"] = line.split(':', 1)[1].strip()
                elif line.startswith('**Character Focus:**'):
                    current_chapter["character_focus"] = [c.strip() for c in line.split(':', 1)[1].strip().split(',')]
                elif line.startswith('**Summary:**'):
                    current_chapter["chapter_summary"] = line.split(':', 1)[1].strip()
            
            # Add the last chapter if it's complete
            if current_chapter and all(field in current_chapter for field in [
                "chapter_number", "chapter_title", "act",
                "key_events", "emotional_turn", "character_focus",
                "chapter_summary"
            ]):
                chapters_data.append(current_chapter)
            
            # Validate we have chapters
            if not chapters_data:
                logger.error("No valid chapters were generated")
                raise ValueError("No valid chapters were generated")
            
            # Log chapter count
            logger.debug(f"Successfully generated {len(chapters_data)} chapters for Act {act_id}")
            
            # Validate chapter count
            expected_count = len(chapter_range)
            if len(chapters_data) != expected_count:
                logger.error(f"Generated {len(chapters_data)} chapters but expected {expected_count}")
                raise ValueError(f"Incorrect number of chapters generated. Expected {expected_count}, got {len(chapters_data)}")
            
            return chapters_data
            
        except Exception as e:
            logger.error(f"Error generating chapters for Act {act_id}: {str(e)}")
            # Fall back to placeholder chapters
            return self._generate_placeholder_chapters(act_id, chapter_range.start, len(chapter_range))
    
    def _generate_placeholder_chapters(self, act: str, start_num: int, count: int) -> List[Dict[str, Any]]:
        """Generate placeholder chapters when LLM generation fails."""
        chapters = []
        for i in range(count):
            chapter_num = start_num + i
            chapter = {
                "chapter_number": chapter_num,
                "chapter_title": f"Placeholder Chapter {chapter_num}",
                "act": act,
                "key_events": [
                    "Placeholder event 1",
                    "Placeholder event 2",
                    "Placeholder event 3"
                ],
                "emotional_turn": "Placeholder emotional turn",
                "character_focus": ["Placeholder character"],
                "chapter_summary": f"Placeholder summary for chapter {chapter_num}"
            }
            chapters.append(chapter)
        return chapters 