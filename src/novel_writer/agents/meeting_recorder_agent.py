"""Meeting Recorder Agent for compiling and documenting idea generation results.

This agent compiles the outputs from various agents in the idea generation workflow
into a well-structured Markdown document that captures all relevant information.
"""

import logging
import os
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from novel_writer.config.llm import LLMConfig
from novel_writer.agents.base_agent import BaseAgent
from novel_writer.utils.file_ops import sanitize_filename

# Initialize logger
logger = logging.getLogger(__name__)

class MeetingRecorderAgent(BaseAgent):
    """Agent responsible for compiling idea generation results into documentation.
    
    This agent takes the outputs from all previous agents in the workflow and 
    synthesizes them into a well-structured Markdown document that captures
    the idea generation process, key decisions, and the final selected pitch
    with enhancements.
    """

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Meeting Recorder Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Meeting Recorder Agent")
        
    async def compile_idea(
        self,
        selected_pitch: Dict[str, str],
        selection_data: Dict[str, Any],
        trope_analysis: Dict[str, Any],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str],
        output_dir: Optional[str] = None
    ) -> Tuple[str, str]:
        """Compile idea generation results into a structured Markdown document.
        
        Takes the winning pitch, selection rationale, and trope analysis to create
        a comprehensive document that captures all relevant information about the 
        generated story idea.
        
        Args:
            selected_pitch: The winning story pitch
            selection_data: Selection rationale and recommendations
            trope_analysis: Analysis of tropes and suggested alternatives
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to explore
            output_dir: Optional directory for saving the output file
            
        Returns:
            Tuple containing (file_path, document_content)
        """
        self._log_method_start(
            "compile_idea", 
            pitch_title=selected_pitch.get("title", "Untitled"),
            genre=genre,
            subgenre=subgenre,
            themes_count=len(themes),
            has_output_dir=output_dir is not None
        )
        
        logger.info(f"Compiling idea document for: {selected_pitch.get('title', 'Untitled')}")
        logger.debug(f"Genre: {genre}, Subgenre: {subgenre}")
        logger.debug(f"Tone: {tone[:50]}..." if len(tone) > 50 else f"Tone: {tone}")
        logger.debug(f"Themes: {', '.join(themes[:3])}" + (f"... and {len(themes)-3} more" if len(themes) > 3 else ""))
        
        # Prepare document components
        doc_title = selected_pitch.get("title", "Untitled")
        doc_id = f"idea_{uuid.uuid4().hex[:8]}"
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        logger.debug(f"Generated doc_id: {doc_id}")
        logger.debug(f"Timestamp: {current_time}")
        
        # Create YAML frontmatter
        frontmatter = self._create_frontmatter(
            doc_id=doc_id,
            title=doc_title,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes,
            selected_pitch=selected_pitch
        )
        
        logger.debug(f"Created frontmatter with {len(frontmatter.split('\n'))} lines")
        
        # Format the document body
        doc_body = self._format_document_body(
            selected_pitch=selected_pitch,
            selection_data=selection_data,
            trope_analysis=trope_analysis,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        logger.debug(f"Created document body with {len(doc_body.split('\n'))} lines")
        
        # Combine components into full document
        doc_content = frontmatter + doc_body
        
        # Determine output file path
        file_path = self._create_output_file_path(
            title=doc_title,
            timestamp=current_time,
            output_dir=output_dir
        )
        
        logger.info(f"Document compiled, saving to: {file_path}")
        
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write document to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            logger.info(f"Document saved successfully to {file_path}")
        except Exception as e:
            error_msg = f"Failed to save document: {str(e)}"
            logger.error(error_msg)
            self._log_method_error("compile_idea", Exception(error_msg))
            
        self._log_method_end("compile_idea", result=f"Document saved to {file_path}")
        return file_path, doc_content
        
    def _create_frontmatter(
        self,
        doc_id: str,
        title: str,
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str],
        selected_pitch: Dict[str, str]
    ) -> str:
        """Create YAML frontmatter for the document.
        
        Args:
            doc_id: Unique identifier for the document
            title: Story title
            genre: Main genre
            subgenre: Specific subgenre
            tone: Story tone
            themes: List of themes
            selected_pitch: The selected story pitch
            
        Returns:
            YAML frontmatter string
        """
        logger.debug("Creating document frontmatter")
        
        # Format themes and tags for YAML
        themes_yaml = ", ".join([f'"{theme}"' for theme in themes])
        tags = [genre, subgenre] + [f"theme:{theme}" for theme in themes] + ["AI_generated"]
        tags_yaml = ", ".join([f'"{tag}"' for tag in tags])
        
        # Extract elevator pitch (hook) from the selected pitch
        elevator_pitch = selected_pitch.get("hook", "")
        
        # Format summary from the premise
        summary = selected_pitch.get("premise", "")
        
        frontmatter = f"""---
doc_type: "idea"
doc_id: "{doc_id}"
status: "winner"
version: "v1"
title: "{title}"
tags: [{tags_yaml}]
elevator_pitch: "{elevator_pitch}"
genre: "{genre}"
subgenre: "{subgenre}"
tone: "{tone}"
themes: [{themes_yaml}]
summary: "{summary}"
created_at: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
---

"""
        logger.superdebug(f"Frontmatter:\n{frontmatter}")
        return frontmatter
        
    def _format_document_body(
        self,
        selected_pitch: Dict[str, str],
        selection_data: Dict[str, Any],
        trope_analysis: Dict[str, Any],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> str:
        """Format the main body of the document.
        
        Args:
            selected_pitch: The winning story pitch
            selection_data: Selection rationale and recommendations
            trope_analysis: Analysis of tropes and suggested alternatives
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to explore
            
        Returns:
            Formatted document body string
        """
        logger.debug("Formatting document body")
        
        # Format themes string
        themes_str = ", ".join(themes)
        
        # Start with title and basic info
        title = selected_pitch.get("title", "Untitled")
        doc_body = [
            f"# {title}",
            "",
            f"**Genre:** {subgenre} ({genre})",
            f"**Tone:** {tone}",
            f"**Themes:** {themes_str}",
            ""
        ]
        
        # Add hook and premise sections
        doc_body.extend([
            "## Elevator Pitch",
            selected_pitch.get("hook", ""),
            "",
            "## Premise",
            selected_pitch.get("premise", ""),
            ""
        ])
        
        # Add story components
        doc_body.extend([
            "## Story Components",
            "",
            "### Main Conflict",
            selected_pitch.get("main_conflict", ""),
            "",
            "### Unique Twist",
            selected_pitch.get("unique_twist", ""),
            ""
        ])
        
        # Add selection rationale if available
        if selection_data and "selection_criteria" in selection_data:
            doc_body.extend([
                "## Selection Criteria",
                ""
            ])
            for criterion in selection_data.get("selection_criteria", []):
                doc_body.append(f"- {criterion}")
            doc_body.append("")
        
        # Add development recommendations if available
        if selection_data and "development_recommendations" in selection_data:
            doc_body.extend([
                "## Development Recommendations",
                ""
            ])
            for recommendation in selection_data.get("development_recommendations", []):
                doc_body.append(f"- {recommendation}")
            doc_body.append("")
        
        # Add potential challenges if available
        if selection_data and "potential_challenges" in selection_data:
            doc_body.extend([
                "## Potential Challenges",
                ""
            ])
            for challenge in selection_data.get("potential_challenges", []):
                doc_body.append(f"- {challenge}")
            doc_body.append("")
        
        # Add trope analysis if available
        if trope_analysis:
            # Add identified tropes
            if "identified_tropes" in trope_analysis and trope_analysis["identified_tropes"]:
                doc_body.extend([
                    "## Trope Analysis",
                    "",
                    "### Identified Tropes",
                    ""
                ])
                for trope in trope_analysis["identified_tropes"]:
                    name = trope.get("name", "")
                    explanation = trope.get("explanation", "")
                    level = trope.get("overuse_level", "")
                    doc_body.append(f"- **{name}** ({level} overuse): {explanation}")
                doc_body.append("")
            
            # Add suggested alternatives
            if "suggested_alternatives" in trope_analysis and trope_analysis["suggested_alternatives"]:
                doc_body.extend([
                    "### Trope Alternatives",
                    ""
                ])
                
                for trope_name, alternatives in trope_analysis["suggested_alternatives"].items():
                    doc_body.append(f"#### For '{trope_name}'")
                    doc_body.append("")
                    
                    for alt in alternatives:
                        alt_name = alt.get("name", "")
                        description = alt.get("description", "")
                        doc_body.append(f"- **{alt_name}**: {description}")
                        
                    doc_body.append("")
                    
            # Add summary if available
            if "summary" in trope_analysis and trope_analysis["summary"]:
                doc_body.extend([
                    "### Summary",
                    "",
                    trope_analysis["summary"],
                    ""
                ])
                
        # Add notes section
        doc_body.extend([
            "## Notes",
            "",
            f"This story idea was generated by AI with the following parameters:",
            f"- Genre: {genre}",
            f"- Subgenre: {subgenre}",
            f"- Tone: {tone}",
            f"- Themes: {themes_str}",
            "",
            f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}",
            ""
        ])
        
        logger.debug(f"Document body sections: {len(doc_body)}")
        formatted_body = "\n".join(doc_body)
        return formatted_body
        
    def _create_output_file_path(
        self,
        title: str,
        timestamp: str,
        output_dir: Optional[str] = None
    ) -> str:
        """Create the output file path for the document.
        
        Args:
            title: Story title
            timestamp: Timestamp string
            output_dir: Optional output directory
            
        Returns:
            Full file path for the document
        """
        logger.debug(f"Creating output file path for '{title}'")
        
        # Sanitize title for use in filenames
        safe_title = sanitize_filename(title)
        logger.debug(f"Sanitized title: '{safe_title}'")
        
        # Create filename
        filename = f"{safe_title}_{timestamp}.md"
        
        # Set up directory structure
        if output_dir:
            # Use specified output directory
            directory = output_dir
            logger.debug(f"Using specified output directory: {output_dir}")
        else:
            # Create default directory structure
            base_dir = os.path.join(os.getcwd(), "ideas")
            story_dir = os.path.join(base_dir, safe_title or "Untitled")
            directory = story_dir
            logger.debug(f"Using default directory structure: {directory}")
            
        # Combine directory and filename
        file_path = os.path.join(directory, filename)
        logger.debug(f"Created file path: {file_path}")
        
        return file_path 