"""
Agent modules for the NovelWriter Idea Generator.
"""

from .base import BaseAgent
from .facilitator import FacilitatorAgent
from .genre_vibe import GenreVibeAgent
from .pitch import PitchAgent
from .critic import CriticAgent
from .improver import ImproverAgent
from .voter import VoterAgent
from .tropemaster import TropemasterAgent
from .recorder import RecorderAgent

__all__ = [
    'BaseAgent',
    'FacilitatorAgent',
    'GenreVibeAgent',
    'PitchAgent',
    'CriticAgent',
    'ImproverAgent',
    'VoterAgent',
    'TropemasterAgent',
    'RecorderAgent'
] 