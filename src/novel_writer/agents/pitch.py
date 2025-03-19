from typing import Any, Dict, List
import random

from .base import BaseAgent

class PitchAgent(BaseAgent):
    """Agent responsible for generating story pitches."""
    
    def __init__(self):
        super().__init__("pitch")
        
    async def run(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate multiple story pitches based on genre, tone, and themes."""
        try:
            self.log_start("pitch generation")
            
            # Generate 3-5 pitches
            num_pitches = random.randint(3, 5)
            pitches = []
            
            for i in range(num_pitches):
                pitch = self._generate_pitch(input_data, i + 1)
                pitches.append(pitch)
                
            self.log_end("pitch generation", count=len(pitches))
            return pitches
            
        except Exception as e:
            self.log_error("pitch generation", e)
            raise
            
    def _generate_pitch(self, input_data: Dict[str, Any], pitch_number: int) -> Dict[str, Any]:
        """Generate a single story pitch."""
        # This is a placeholder - in the actual implementation, this would use
        # more sophisticated logic or AI to generate a compelling pitch
        pitch_templates = [
            "In a {genre} world where {theme1} and {theme2} collide, {character} must {conflict}.",
            "When {event} threatens {setting}, {character} discovers {secret} that changes everything.",
            "A {character} with {ability} must navigate a world where {theme1} and {theme2} are at odds.",
            "In a {tone} tale of {genre}, {character} faces {conflict} while grappling with {theme1}.",
            "The {setting} holds a secret: {secret}. Now {character} must {conflict} before {stakes}."
        ]
        
        # Generate placeholder content
        character_types = ['scientist', 'warrior', 'explorer', 'detective', 'artist', 'rebel']
        abilities = ['unique powers', 'special knowledge', 'rare skills', 'mysterious past']
        events = ['catastrophe', 'discovery', 'invasion', 'revolution', 'mystery']
        secrets = ['ancient technology', 'forbidden knowledge', 'hidden truth', 'lost civilization']
        settings = ['distant planet', 'magical realm', 'post-apocalyptic city', 'floating island']
        conflicts = ['save their world', 'uncover the truth', 'defeat the enemy', 'find redemption']
        stakes = ['it\'s too late', 'the world ends', 'everyone dies', 'hope is lost']
        
        template = random.choice(pitch_templates)
        pitch = template.format(
            genre=input_data['genre'],
            theme1=input_data['themes'][0],
            theme2=input_data['themes'][1],
            tone=input_data['tone'],
            character=random.choice(character_types),
            ability=random.choice(abilities),
            event=random.choice(events),
            secret=random.choice(secrets),
            setting=random.choice(settings),
            conflict=random.choice(conflicts),
            stakes=random.choice(stakes)
        )
        
        return {
            'id': f'pitch_{pitch_number}',
            'content': pitch,
            'genre': input_data['genre'],
            'tone': input_data['tone'],
            'themes': input_data['themes']
        } 