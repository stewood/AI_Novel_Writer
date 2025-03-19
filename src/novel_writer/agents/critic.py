from typing import Any, Dict, List
import random

from .base import BaseAgent

class CriticAgent(BaseAgent):
    """Agent responsible for evaluating story pitches."""
    
    def __init__(self):
        super().__init__("critic")
        
    async def run(self, pitches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate each pitch based on multiple criteria."""
        try:
            self.log_start("pitch evaluation")
            
            evaluated_pitches = []
            for pitch in pitches:
                evaluation = self._evaluate_pitch(pitch)
                evaluated_pitches.append({
                    **pitch,
                    'evaluation': evaluation
                })
                
            self.log_end("pitch evaluation", count=len(evaluated_pitches))
            return evaluated_pitches
            
        except Exception as e:
            self.log_error("pitch evaluation", e)
            raise
            
    def _evaluate_pitch(self, pitch: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single pitch based on multiple criteria."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to evaluate the pitch
        
        # Generate random scores between 1 and 10
        scores = {
            'originality': random.randint(1, 10),
            'emotional_impact': random.randint(1, 10),
            'genre_fit': random.randint(1, 10),
            'uniqueness': random.randint(1, 10)
        }
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        
        # Generate feedback
        feedback = self._generate_feedback(scores, pitch)
        
        return {
            'scores': scores,
            'overall_score': overall_score,
            'feedback': feedback,
            'needs_improvement': overall_score < 7.0
        }
        
    def _generate_feedback(self, scores: Dict[str, float], pitch: Dict[str, Any]) -> Dict[str, str]:
        """Generate feedback for each evaluation criterion."""
        feedback = {}
        
        # Generate feedback based on scores
        for criterion, score in scores.items():
            if score < 4:
                feedback[criterion] = f"Needs significant improvement in {criterion.replace('_', ' ')}"
            elif score < 7:
                feedback[criterion] = f"Could be enhanced in {criterion.replace('_', ' ')}"
            else:
                feedback[criterion] = f"Strong in {criterion.replace('_', ' ')}"
                
        return feedback 