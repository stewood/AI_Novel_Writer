from typing import Any, Dict, List
import random

from .base import BaseAgent

class VoterAgent(BaseAgent):
    """Agent responsible for selecting the best pitch."""
    
    def __init__(self):
        super().__init__("voter")
        
    async def run(self, improved_pitches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best pitch from the improved pitches."""
        try:
            self.log_start("pitch selection")
            
            # Score each pitch based on multiple factors
            scored_pitches = []
            for pitch in improved_pitches:
                score = self._score_pitch(pitch)
                scored_pitches.append({
                    **pitch,
                    'selection_score': score
                })
                
            # Sort pitches by score
            scored_pitches.sort(key=lambda x: x['selection_score'], reverse=True)
            
            # Select the winning pitch
            winning_pitch = scored_pitches[0]
            
            self.log_end("pitch selection", winner_id=winning_pitch['id'])
            return winning_pitch
            
        except Exception as e:
            self.log_error("pitch selection", e)
            raise
            
    def _score_pitch(self, pitch: Dict[str, Any]) -> float:
        """Score a pitch based on multiple factors."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to score the pitch
        
        # Get the evaluation scores
        evaluation = pitch['evaluation']
        scores = evaluation['scores']
        
        # Calculate base score from evaluation
        base_score = evaluation['overall_score']
        
        # Add bonus for improvements
        improvement_bonus = 0.0
        if pitch.get('is_improved', False):
            improvement_bonus = 0.5
            
        # Add bonus for strong emotional impact
        emotional_bonus = 0.0
        if scores['emotional_impact'] >= 8:
            emotional_bonus = 0.3
            
        # Add bonus for high originality
        originality_bonus = 0.0
        if scores['originality'] >= 8:
            originality_bonus = 0.3
            
        # Calculate final score
        final_score = base_score + improvement_bonus + emotional_bonus + originality_bonus
        
        return min(10.0, final_score)  # Cap at 10.0 