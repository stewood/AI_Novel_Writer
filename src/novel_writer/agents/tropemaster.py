from typing import Any, Dict, List
import random

from .base import BaseAgent

class TropemasterAgent(BaseAgent):
    """Agent responsible for analyzing tropes and suggesting improvements."""
    
    def __init__(self):
        super().__init__("tropemaster")
        self.common_tropes = self._load_common_tropes()
        
    def _load_common_tropes(self) -> Dict[str, List[str]]:
        """Load common tropes for different genres."""
        # This is a placeholder - in the actual implementation, this would load
        # from a comprehensive database of tropes
        return {
            'science_fiction': [
                'The Chosen One',
                'Time Travel Paradox',
                'Alien Invasion',
                'Dystopian Society',
                'Space Opera',
                'First Contact',
                'AI Rebellion',
                'Post-Apocalyptic World',
                'Parallel Universe',
                'Scientific Discovery'
            ],
            'fantasy': [
                'The Hero\'s Journey',
                'Magic System',
                'Chosen One',
                'Dark Lord',
                'Mystical Artifact',
                'Hidden World',
                'Rags to Riches',
                'Good vs Evil',
                'Mentor Figure',
                'Prophecy'
            ],
            'custom': [
                'Love Triangle',
                'Redemption Arc',
                'Mystery Plot',
                'Coming of Age',
                'Revenge Story',
                'Fish out of Water',
                'Rags to Riches',
                'Underdog Story',
                'Mysterious Past',
                'Hidden Identity'
            ]
        }
        
    async def run(self, winning_pitch: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the winning pitch for tropes and suggest improvements."""
        try:
            self.log_start("trope analysis")
            
            # Analyze the pitch for tropes
            detected_tropes = self._detect_tropes(winning_pitch)
            
            # Generate suggestions for improvement
            suggestions = self._generate_suggestions(detected_tropes, winning_pitch)
            
            result = {
                'detected_tropes': detected_tropes,
                'suggestions': suggestions
            }
            
            self.log_end("trope analysis", trope_count=len(detected_tropes))
            return result
            
        except Exception as e:
            self.log_error("trope analysis", e)
            raise
            
    def _detect_tropes(self, pitch: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect tropes present in the pitch."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to detect tropes
        
        # Get relevant tropes for the genre
        genre_tropes = self.common_tropes.get(pitch['genre'], self.common_tropes['custom'])
        
        # Randomly select 2-4 tropes that might be present
        num_tropes = random.randint(2, 4)
        selected_tropes = random.sample(genre_tropes, num_tropes)
        
        # Create trope objects with impact assessment
        detected_tropes = []
        for trope in selected_tropes:
            impact = random.choice(['positive', 'neutral', 'negative'])
            detected_tropes.append({
                'name': trope,
                'impact': impact,
                'description': f"Analysis of how {trope} affects the story"
            })
            
        return detected_tropes
        
    def _generate_suggestions(self, detected_tropes: List[Dict[str, Any]], pitch: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggestions for improving or subverting tropes."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to generate suggestions
        
        suggestions = []
        for trope in detected_tropes:
            if trope['impact'] == 'negative':
                # Generate a suggestion to improve or subvert the trope
                suggestion = {
                    'trope': trope['name'],
                    'suggestion': f"Consider subverting or improving the {trope['name']} trope by...",
                    'impact': 'improvement'
                }
                suggestions.append(suggestion)
                
        return suggestions 