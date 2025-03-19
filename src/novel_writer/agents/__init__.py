"""
Agent modules for the NovelWriter Idea Generator.

This package contains all the specialized AI agents used in the novel_writer
application. Each agent has a specific role in the idea generation process:

- FacilitatorAgent: Orchestrates the overall process and coordinates other agents
- GenreVibeAgent: Selects genres and generates appropriate tone and themes
- PitchGeneratorAgent: Creates multiple story pitches based on genre/tone/themes
- CriticAgent: Evaluates story pitches based on various criteria
- ImproverAgent: Enhances pitches that need improvement
- VoterAgent: Selects the best pitch from multiple candidates
- TropemasterAgent: Identifies tropes and suggests creative alternatives
- MeetingRecorderAgent: Creates a final document with all the generated content
"""

from .base_agent import BaseAgent
from .facilitator_agent import FacilitatorAgent
from .genre_vibe_agent import GenreVibeAgent
from .pitch_generator_agent import PitchGeneratorAgent
from .critic_agent import CriticAgent
from .improver_agent import ImproverAgent
from .voter_agent import VoterAgent
from .tropemaster_agent import TropemasterAgent
from .meeting_recorder_agent import MeetingRecorderAgent

__all__ = [
    'BaseAgent',
    'FacilitatorAgent',
    'GenreVibeAgent',
    'PitchGeneratorAgent',
    'CriticAgent',
    'ImproverAgent',
    'VoterAgent',
    'TropemasterAgent',
    'MeetingRecorderAgent'
] 