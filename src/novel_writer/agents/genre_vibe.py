import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseAgent

class GenreVibeAgent(BaseAgent):
    """Agent responsible for genre selection and vibe generation."""
    
    def __init__(self):
        super().__init__("genre_vibe")
        self.subgenres = self._load_subgenres()
        
    def _load_subgenres(self) -> Dict[str, List[str]]:
        """Load the subgenres from the JSON file."""
        subgenres_path = Path(__file__).parent.parent / "data" / "subgenres.json"
        with open(subgenres_path, 'r') as f:
            return json.load(f)
            
    def _select_random_genre(self) -> Dict[str, str]:
        """Select a random genre and subgenre."""
        category = random.choice(list(self.subgenres.keys()))
        subgenre = random.choice(self.subgenres[category])
        self.log_info(f"Selected genre: {subgenre} ({category})")
        return {
            'category': category,
            'subgenre': subgenre
        }
        
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate genre, tone, and themes for the story."""
        try:
            self.log_start("genre and vibe generation")
            
            # Use provided genre or select randomly
            genre_info = (
                {'category': 'custom', 'subgenre': input_data['genre']}
                if input_data.get('genre')
                else self._select_random_genre()
            )
            
            # Use provided tone or generate one
            tone = input_data.get('tone') or self._generate_tone(genre_info)
            
            # Use provided themes or generate them
            themes = (
                input_data.get('themes')
                or self._generate_themes(genre_info, tone)
            )
            
            result = {
                'genre': genre_info['subgenre'],
                'category': genre_info['category'],
                'tone': tone,
                'themes': themes
            }
            
            self.log_end("genre and vibe generation", result=result)
            return result
            
        except Exception as e:
            self.log_error("genre and vibe generation", e)
            raise
            
    def _generate_tone(self, genre_info: Dict[str, str]) -> str:
        """Generate an appropriate tone based on the genre."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to generate an appropriate tone
        tones = {
            'science_fiction': ['optimistic', 'pessimistic', 'neutral', 'wonder-filled'],
            'fantasy': ['epic', 'dark', 'whimsical', 'mysterious'],
            'custom': ['dramatic', 'light', 'serious', 'playful']
        }
        return random.choice(tones.get(genre_info['category'], tones['custom']))
        
    def _generate_themes(self, genre_info: Dict[str, str], tone: str) -> List[str]:
        """Generate appropriate themes based on genre and tone."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to generate appropriate themes
        themes = {
            'science_fiction': [
                'exploration', 'technology', 'humanity', 'progress',
                'society', 'identity', 'survival', 'discovery'
            ],
            'fantasy': [
                'power', 'destiny', 'good vs evil', 'coming of age',
                'friendship', 'loyalty', 'magic', 'adventure'
            ],
            'custom': [
                'love', 'loss', 'redemption', 'justice',
                'freedom', 'truth', 'courage', 'hope'
            ]
        }
        base_themes = themes.get(genre_info['category'], themes['custom'])
        return random.sample(base_themes, min(5, len(base_themes))) 