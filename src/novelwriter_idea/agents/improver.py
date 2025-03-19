from typing import Any, Dict, List
import random

from .base import BaseAgent

class ImproverAgent(BaseAgent):
    """Agent responsible for improving low-scoring pitches."""
    
    def __init__(self):
        super().__init__("improver")
        
    async def run(self, evaluated_pitches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Improve pitches that received low scores."""
        try:
            self.log_start("pitch improvement")
            
            improved_pitches = []
            for pitch in evaluated_pitches:
                if pitch['evaluation']['needs_improvement']:
                    improved_pitch = self._improve_pitch(pitch)
                    improved_pitches.append(improved_pitch)
                else:
                    improved_pitches.append(pitch)
                    
            self.log_end("pitch improvement", count=len(improved_pitches))
            return improved_pitches
            
        except Exception as e:
            self.log_error("pitch improvement", e)
            raise
            
    def _improve_pitch(self, pitch: Dict[str, Any]) -> Dict[str, Any]:
        """Improve a single pitch based on its evaluation."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to improve the pitch
        
        # Get the original content and evaluation
        original_content = pitch['content']
        evaluation = pitch['evaluation']
        
        # Generate improvement suggestions based on low scores
        improvements = []
        for criterion, score in evaluation['scores'].items():
            if score < 7:
                improvements.append(self._generate_improvement(criterion, pitch))
                
        # Apply improvements to the pitch
        improved_content = self._apply_improvements(original_content, improvements)
        
        return {
            **pitch,
            'content': improved_content,
            'improvements': improvements,
            'is_improved': True
        }
        
    def _generate_improvement(self, criterion: str, pitch: Dict[str, Any]) -> Dict[str, Any]:
        """Generate improvement suggestions for a specific criterion."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to generate improvements
        
        improvements = {
            'originality': [
                'Add a unique twist to the premise',
                'Introduce an unexpected element',
                'Subvert common genre tropes'
            ],
            'emotional_impact': [
                'Add personal stakes',
                'Include emotional conflict',
                'Develop character motivation'
            ],
            'genre_fit': [
                'Strengthen genre elements',
                'Add genre-specific details',
                'Emphasize genre conventions'
            ],
            'uniqueness': [
                'Add distinctive world-building elements',
                'Create a unique character perspective',
                'Introduce an original concept'
            ]
        }
        
        return {
            'criterion': criterion,
            'suggestion': random.choice(improvements.get(criterion, ['Enhance the overall concept'])),
            'applied': False
        }
        
    def _apply_improvements(self, content: str, improvements: List[Dict[str, Any]]) -> str:
        """Apply the improvements to the pitch content."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to apply improvements
        
        # For now, just append the improvements as notes
        improved_content = content + "\n\nImprovements applied:\n"
        for improvement in improvements:
            improved_content += f"- {improvement['suggestion']}\n"
            improvement['applied'] = True
            
        return improved_content 