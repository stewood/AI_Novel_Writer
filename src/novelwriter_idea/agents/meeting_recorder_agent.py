"""Meeting Recorder Agent for compiling and formatting story idea outputs."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from novelwriter_idea.agents.base_agent import BaseAgent
from novelwriter_idea.config.llm import LLMConfig

class MeetingRecorderAgent(BaseAgent):
    """Agent responsible for compiling and formatting the final story idea output."""

    def __init__(self, llm_config: Optional[LLMConfig] = None, logger: Optional[logging.Logger] = None):
        """Initialize the Meeting Recorder Agent.
        
        Args:
            llm_config: Optional LLM configuration for generating additional content
            logger: Optional logger instance
        """
        super().__init__(llm_config=llm_config, logger=logger)
        self.logger.info("Initializing Meeting Recorder Agent")

    def _generate_doc_id(self, title: str) -> str:
        """Generate a unique document ID.
        
        Args:
            title: Story title to incorporate into ID
        
        Returns:
            Unique document ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # YYYYMMDDhhmmss format
        sanitized_title = "".join(c.lower() for c in title if c.isalnum())[:30]
        return f"idea_{sanitized_title}_{timestamp}"

    def _generate_frontmatter(self, 
        title: str,
        genre: str,
        tone: str,
        themes: List[str],
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate YAML frontmatter for the document.
        
        Args:
            title: Story title
            genre: Story genre
            tone: Story tone/mood
            themes: List of story themes
            tags: Optional additional tags
        
        Returns:
            Dictionary of frontmatter fields
        """
        doc_id = self._generate_doc_id(title)
        
        # Combine all tags
        all_tags = [
            genre.lower().replace(" ", "_"),
            tone.lower().replace(" ", "_"),
            "ai_generated"
        ]
        all_tags.extend(t.lower().replace(" ", "_") for t in themes)
        if tags:
            all_tags.extend(t.lower().replace(" ", "_") for t in tags)
        
        return {
            "doc_type": "idea",
            "doc_id": doc_id,
            "status": "winner",
            "version": "v1",
            "tags": sorted(list(set(all_tags))),  # Remove duplicates
            "title": title,
            "genre": genre,
            "tone": tone,
            "themes": themes
        }

    def _format_trope_section(self, trope_analysis: Dict[str, Any]) -> str:
        """Format the trope analysis section.
        
        Args:
            trope_analysis: Dictionary containing trope analysis data
        
        Returns:
            Formatted markdown string
        """
        sections = []
        
        # Identified Tropes
        sections.append("## Identified Tropes\n")
        for trope in trope_analysis["identified_tropes"]:
            sections.append(f"### {trope['trope']}\n")
            sections.append(f"- **Description**: {trope['description']}")
            sections.append(f"- **Common Usage**: {trope['common_usage']}")
            sections.append(f"- **Current Handling**: {trope['current_handling']}")
            sections.append(f"- **Originality Score**: {trope['originality_score']}/10\n")
        
        # Subversion Suggestions
        sections.append("## Trope Subversion Suggestions\n")
        for subversion in trope_analysis["subversion_suggestions"]:
            sections.append(f"### {subversion['trope']}")
            sections.append(f"- **Suggestion**: {subversion['suggestion']}")
            sections.append(f"- **Impact**: {subversion['impact']}\n")
        
        # Original Elements
        sections.append("## Original Elements\n")
        for element in trope_analysis["original_elements"]:
            sections.append(f"- {element}")
        sections.append("\n")
        
        # Enhancement Suggestions
        sections.append("## Enhancement Suggestions\n")
        for enhancement in trope_analysis["enhancement_suggestions"]:
            sections.append(f"### {enhancement['element']}")
            sections.append(f"- **Suggestion**: {enhancement['suggestion']}")
            sections.append(f"- **Rationale**: {enhancement['rationale']}\n")
        
        return "\n".join(sections)

    async def process(self,
        pitch: Dict[str, str],
        genre: str,
        tone: str,
        themes: List[str],
        trope_analysis: Dict[str, Any],
        output_dir: Optional[Path] = None,
        additional_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compile and format the final story idea document.
        
        Args:
            pitch: Dictionary containing the story pitch
            genre: Story genre
            tone: Story tone/mood
            themes: List of story themes
            trope_analysis: Dictionary containing trope analysis
            output_dir: Optional output directory path
            additional_tags: Optional additional tags to include
        
        Returns:
            Dictionary containing status and file path
        """
        try:
            self.logger.info(f"Compiling story idea document for: {pitch['title']}")
            
            # Generate frontmatter
            frontmatter = self._generate_frontmatter(
                title=pitch['title'],
                genre=genre,
                tone=tone,
                themes=themes,
                tags=additional_tags
            )
            
            # Build document sections
            sections = []
            
            # Add frontmatter
            sections.append("---")
            sections.append(yaml.dump(frontmatter, sort_keys=False))
            sections.append("---\n")
            
            # Add pitch sections
            sections.append(f"# {pitch['title']}\n")
            sections.append("## Elevator Pitch")
            sections.append(pitch['hook'])
            sections.append("\n## Concept")
            sections.append(pitch['concept'])
            sections.append("\n## Core Conflict")
            sections.append(pitch['conflict'])
            if 'twist' in pitch:
                sections.append("\n## Key Twist")
                sections.append(pitch['twist'])
            sections.append("\n")
            
            # Add trope analysis
            sections.append(self._format_trope_section(trope_analysis))
            
            # Combine into final document
            document = "\n".join(sections)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            sanitized_title = "".join(c.lower() for c in pitch['title'] if c.isalnum())
            filename = f"{sanitized_title}_{timestamp}.md"
            
            # Determine output path
            if output_dir:
                output_path = output_dir / filename
            else:
                output_path = Path.cwd() / "ideas" / sanitized_title / filename
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            output_path.write_text(document, encoding='utf-8')
            
            self.logger.info(f"Successfully wrote story idea to: {output_path}")
            
            return {
                "status": "success",
                "file_path": str(output_path),
                "doc_id": frontmatter["doc_id"]
            }
            
        except Exception as e:
            self.logger.error(f"Error compiling story idea document: {str(e)}")
            raise 