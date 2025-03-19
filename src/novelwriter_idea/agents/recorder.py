import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from slugify import slugify

from .base import BaseAgent

class RecorderAgent(BaseAgent):
    """Agent responsible for recording the final idea in Markdown format."""
    
    def __init__(self):
        super().__init__("recorder")
        
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compile and save the final idea as a Markdown file."""
        try:
            self.log_start("idea recording")
            
            # Extract data from input
            winning_pitch = input_data['winning_pitch']
            genre_vibe = input_data['genre_vibe']
            trope_analysis = input_data['trope_analysis']
            output_path = input_data.get('output_path')
            
            # Generate the markdown content
            content = self._generate_markdown(
                winning_pitch,
                genre_vibe,
                trope_analysis
            )
            
            # Determine the output path
            final_path = self._determine_output_path(
                winning_pitch,
                output_path
            )
            
            # Save the file
            self._save_file(final_path, content)
            
            self.log_end("idea recording", output_path=str(final_path))
            return {'output_path': str(final_path)}
            
        except Exception as e:
            self.log_error("idea recording", e)
            raise
            
    def _generate_markdown(
        self,
        winning_pitch: Dict[str, Any],
        genre_vibe: Dict[str, Any],
        trope_analysis: Dict[str, Any]
    ) -> str:
        """Generate the markdown content for the idea."""
        # Generate a unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_id = f"idea_{timestamp}"
        
        # Extract title from pitch or use "Untitled"
        title = winning_pitch.get('title', 'Untitled')
        
        # Generate YAML frontmatter
        frontmatter = {
            'doc_type': 'idea',
            'doc_id': doc_id,
            'status': 'winner',
            'version': 'v1',
            'tags': [
                genre_vibe['genre'],
                genre_vibe['tone'],
                *genre_vibe['themes'],
                'AI_generated'
            ],
            'title': title,
            'elevator_pitch': winning_pitch['content'],
            'genre': genre_vibe['genre'],
            'tone': genre_vibe['tone'],
            'themes': genre_vibe['themes'],
            'summary': winning_pitch.get('summary', ''),
            'notes': winning_pitch.get('notes', ''),
            'tropes': [trope['name'] for trope in trope_analysis['detected_tropes']],
            'trope_suggestions': [
                suggestion['suggestion']
                for suggestion in trope_analysis['suggestions']
            ]
        }
        
        # Convert to YAML
        yaml_content = self._dict_to_yaml(frontmatter)
        
        # Combine everything into the final markdown
        markdown = f"""---
{yaml_content}
---

# {title}

## Elevator Pitch
{winning_pitch['content']}

## Summary
{winning_pitch.get('summary', 'Summary to be expanded...')}

## Genre & Themes
- **Genre:** {genre_vibe['genre']}
- **Tone:** {genre_vibe['tone']}
- **Themes:** {', '.join(genre_vibe['themes'])}

## Trope Analysis
### Detected Tropes
{self._format_tropes(trope_analysis['detected_tropes'])}

### Improvement Suggestions
{self._format_suggestions(trope_analysis['suggestions'])}

## Notes
{winning_pitch.get('notes', 'Additional notes and insights...')}
"""
        return markdown
        
    def _determine_output_path(self, winning_pitch: Dict[str, Any], output_path: Path = None) -> Path:
        """Determine the final output path for the idea file."""
        # Get title or use "untitled"
        title = winning_pitch.get('title', 'untitled')
        slug = slugify(title)
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        if output_path:
            # If output path is provided, use it
            final_path = Path(output_path)
        else:
            # Create ideas directory structure
            ideas_dir = Path("ideas") / slug
            ideas_dir.mkdir(parents=True, exist_ok=True)
            final_path = ideas_dir / f"{slug}-{timestamp}.md"
            
        return final_path
        
    def _save_file(self, path: Path, content: str):
        """Save the markdown content to a file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def _dict_to_yaml(self, data: Dict[str, Any]) -> str:
        """Convert a dictionary to YAML format."""
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
        
    def _format_tropes(self, tropes: list) -> str:
        """Format the detected tropes for markdown."""
        lines = []
        for trope in tropes:
            lines.append(f"- **{trope['name']}** ({trope['impact']})")
            lines.append(f"  {trope['description']}")
        return "\n".join(lines)
        
    def _format_suggestions(self, suggestions: list) -> str:
        """Format the improvement suggestions for markdown."""
        lines = []
        for suggestion in suggestions:
            lines.append(f"- **{suggestion['trope']}**")
            lines.append(f"  {suggestion['suggestion']}")
        return "\n".join(lines) 