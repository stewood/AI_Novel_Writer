from typing import Any, Dict, List
from pathlib import Path

from .base import BaseAgent
from .genre_vibe import GenreVibeAgent
from .pitch import PitchAgent
from .critic import CriticAgent
from .improver import ImproverAgent
from .voter import VoterAgent
from .tropemaster import TropemasterAgent
from .recorder import RecorderAgent

class FacilitatorAgent(BaseAgent):
    """The main orchestrator agent that coordinates the idea generation process."""
    
    def __init__(self):
        super().__init__("facilitator")
        self.genre_vibe_agent = GenreVibeAgent()
        self.pitch_agent = PitchAgent()
        self.critic_agent = CriticAgent()
        self.improver_agent = ImproverAgent()
        self.voter_agent = VoterAgent()
        self.tropemaster_agent = TropemasterAgent()
        self.recorder_agent = RecorderAgent()
        
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete idea generation workflow."""
        try:
            self.log_start("idea generation process")
            
            # Step 1: Generate genre, tone, and themes
            genre_vibe_result = await self.genre_vibe_agent.run(input_data)
            self.log_debug("Genre and vibe generated", result=genre_vibe_result)
            
            # Step 2: Generate multiple pitches
            pitches = await self.pitch_agent.run(genre_vibe_result)
            self.log_debug("Pitches generated", count=len(pitches))
            
            # Step 3: Evaluate pitches
            evaluations = await self.critic_agent.run(pitches)
            self.log_debug("Pitches evaluated", count=len(evaluations))
            
            # Step 4: Improve low-scoring pitches
            improved_pitches = await self.improver_agent.run(evaluations)
            self.log_debug("Pitches improved", count=len(improved_pitches))
            
            # Step 5: Select the best pitch
            winning_pitch = await self.voter_agent.run(improved_pitches)
            self.log_debug("Winning pitch selected", pitch=winning_pitch)
            
            # Step 6: Analyze tropes
            trope_analysis = await self.tropemaster_agent.run(winning_pitch)
            self.log_debug("Trope analysis completed", analysis=trope_analysis)
            
            # Step 7: Record the final result
            result = await self.recorder_agent.run({
                'winning_pitch': winning_pitch,
                'genre_vibe': genre_vibe_result,
                'trope_analysis': trope_analysis,
                'output_path': input_data.get('output_path')
            })
            
            self.log_end("idea generation process", output_path=result['output_path'])
            return result
            
        except Exception as e:
            self.log_error("idea generation process", e)
            raise 