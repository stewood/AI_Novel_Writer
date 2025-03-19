"""Facilitator Agent for orchestrating the story idea generation process."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from novelwriter_idea.agents.base_agent import BaseAgent
from novelwriter_idea.agents.critic_agent import CriticAgent
from novelwriter_idea.agents.genre_vibe_agent import GenreVibeAgent
from novelwriter_idea.agents.improver_agent import ImproverAgent
from novelwriter_idea.agents.meeting_recorder_agent import MeetingRecorderAgent
from novelwriter_idea.agents.pitch_generator_agent import PitchGeneratorAgent
from novelwriter_idea.agents.tropemaster_agent import TropemasterAgent
from novelwriter_idea.agents.voter_agent import VoterAgent
from novelwriter_idea.config.llm import LLMConfig

class GenerationStage(Enum):
    """Stages of the story idea generation process."""
    INITIAL = "initial"
    GENRE_SELECTION = "genre_selection"
    PITCH_GENERATION = "pitch_generation"
    CRITIC_EVALUATION = "critic_evaluation"
    PITCH_IMPROVEMENT = "pitch_improvement"
    PITCH_SELECTION = "pitch_selection"
    TROPE_ANALYSIS = "trope_analysis"
    DOCUMENTATION = "documentation"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class ConversationState:
    """Tracks the current state of the idea generation process."""
    stage: GenerationStage = GenerationStage.INITIAL
    genre: Optional[str] = None
    tone: Optional[str] = None
    themes: List[str] = field(default_factory=list)
    pitches: List[Dict[str, Any]] = field(default_factory=list)
    evaluations: List[Dict[str, Any]] = field(default_factory=list)
    improved_pitches: List[Dict[str, Any]] = field(default_factory=list)
    selected_pitch: Optional[Dict[str, Any]] = None
    selection_data: Optional[Dict[str, Any]] = None
    trope_analysis: Optional[Dict[str, Any]] = None
    output_path: Optional[Path] = None
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)

class FacilitatorAgent(BaseAgent):
    """Agent responsible for orchestrating the story idea generation process."""
    
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        logger: Optional[logging.Logger] = None,
        output_dir: Optional[Path] = None
    ):
        """Initialize the Facilitator Agent.
        
        Args:
            llm_config: Configuration for the LLM client
            logger: Optional logger instance
            output_dir: Optional output directory for generated files
        """
        super().__init__(llm_config, logger)
        self.logger.name = "FacilitatorAgent"
        self.logger.info("Initializing Facilitator Agent")
        
        # Initialize all sub-agents with their own loggers
        self.genre_vibe_agent = GenreVibeAgent(llm_config)
        self.pitch_generator_agent = PitchGeneratorAgent(llm_config)
        self.critic_agent = CriticAgent(llm_config)
        self.improver_agent = ImproverAgent(llm_config)
        self.voter_agent = VoterAgent(llm_config)
        self.tropemaster_agent = TropemasterAgent(llm_config)
        self.meeting_recorder_agent = MeetingRecorderAgent(llm_config)
        
        # Set output directory
        self.output_dir = output_dir or Path.cwd() / "ideas"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize conversation state
        self.state = ConversationState()
    
    def _update_state(self, **kwargs) -> None:
        """Update the conversation state with new information.
        
        Args:
            **kwargs: Key-value pairs to update in the state
        """
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        self.state.last_update = datetime.now()
    
    async def _handle_error(self, error: Exception, stage: GenerationStage) -> None:
        """Handle errors during the generation process.
        
        Args:
            error: The exception that occurred
            stage: The stage where the error occurred
        """
        error_msg = f"{stage.value.replace('_', ' ').title()} failed: {str(error)}"
        self.logger.error(error_msg)
        self._update_state(
            stage=GenerationStage.ERROR,
            error=error_msg
        )
    
    async def _run_genre_selection(self, genre: Optional[str] = None) -> None:
        """Run the genre and vibe selection stage.
        
        Args:
            genre: Optional specific genre to use
        """
        try:
            self.logger.info("Starting genre and vibe selection")
            result = await self.genre_vibe_agent.process(genre=genre)
            
            if result["status"] == "success":
                self._update_state(
                    stage=GenerationStage.PITCH_GENERATION,
                    genre=result["genre"],
                    tone=result["tone"],
                    themes=result["themes"]
                )
                self.logger.info("Completed genre and vibe selection")
            else:
                raise Exception(f"Genre selection failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            await self._handle_error(e, GenerationStage.GENRE_SELECTION)
            raise
    
    async def _run_pitch_generation(self) -> None:
        """Run the pitch generation stage."""
        try:
            self.logger.info("Starting pitch generation")
            result = await self.pitch_generator_agent.process(
                genre=self.state.genre,
                tone=self.state.tone,
                themes=self.state.themes
            )
            
            if result["status"] == "success":
                self._update_state(
                    stage=GenerationStage.CRITIC_EVALUATION,
                    pitches=result["pitches"]
                )
                self.logger.info("Completed pitch generation")
            else:
                raise Exception(f"Pitch generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            await self._handle_error(e, GenerationStage.PITCH_GENERATION)
            raise
    
    async def _run_critic_evaluation(self) -> None:
        """Run the critic evaluation stage."""
        try:
            self.logger.info("Starting critic evaluation")
            result = await self.critic_agent.process(
                pitches=self.state.pitches,
                genre=self.state.genre,
                tone=self.state.tone,
                themes=self.state.themes
            )
            
            if result["status"] == "success":
                self._update_state(
                    stage=GenerationStage.PITCH_IMPROVEMENT,
                    evaluations=result["evaluations"]
                )
                self.logger.info("Completed critic evaluations")
            else:
                raise Exception(f"Critic evaluation failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            await self._handle_error(e, GenerationStage.CRITIC_EVALUATION)
            raise
    
    async def _run_pitch_improvement(self) -> None:
        """Run the pitch improvement stage."""
        try:
            self.logger.info("Starting pitch improvement")
            improved_pitches = []
            
            for pitch, evaluation in zip(self.state.pitches, self.state.evaluations):
                result = await self.improver_agent.process(
                    pitch=pitch,
                    evaluation=evaluation,
                    genre=self.state.genre,
                    tone=self.state.tone,
                    themes=self.state.themes
                )
                
                if result["status"] == "success":
                    improved_pitches.append(result["improved_pitch"])
                else:
                    raise Exception(f"Pitch improvement failed: {result.get('error', 'Unknown error')}")
            
            self._update_state(
                stage=GenerationStage.PITCH_SELECTION,
                improved_pitches=improved_pitches
            )
            self.logger.info("Completed pitch improvements")
            
        except Exception as e:
            await self._handle_error(e, GenerationStage.PITCH_IMPROVEMENT)
            raise
    
    async def _run_pitch_selection(self) -> None:
        """Run the pitch selection stage."""
        try:
            self.logger.info("Starting pitch selection")
            result = await self.voter_agent.process(
                pitches=self.state.improved_pitches,
                evaluations=self.state.evaluations,
                genre=self.state.genre,
                tone=self.state.tone,
                themes=self.state.themes
            )
            
            if result["status"] == "success":
                selected_index = result["selected_index"]
                selected_pitch = self.state.improved_pitches[selected_index]
                selected_pitch["rationale"] = result["rationale"]
                
                self._update_state(
                    stage=GenerationStage.TROPE_ANALYSIS,
                    selected_pitch=selected_pitch,
                    selection_data={
                        "rationale": result["rationale"],
                        "potential_challenges": result["potential_challenges"],
                        "development_recommendations": result["development_recommendations"]
                    }
                )
                self.logger.info("Completed pitch selection")
            else:
                raise Exception(f"Pitch selection failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            await self._handle_error(e, GenerationStage.PITCH_SELECTION)
            raise
    
    async def _run_trope_analysis(self) -> None:
        """Run the trope analysis stage."""
        try:
            self.logger.info("Starting trope analysis")
            result = await self.tropemaster_agent.process(
                pitch=self.state.selected_pitch,
                genre=self.state.genre,
                tone=self.state.tone,
                themes=self.state.themes
            )
            
            if result["status"] == "success":
                self._update_state(
                    stage=GenerationStage.DOCUMENTATION,
                    trope_analysis=result["analysis"]
                )
                self.logger.info("Completed trope analysis")
            else:
                raise Exception(f"Trope analysis failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            await self._handle_error(e, GenerationStage.TROPE_ANALYSIS)
            raise
    
    async def _run_documentation(self) -> None:
        """Run the documentation stage."""
        try:
            self.logger.info("Starting documentation")
            result = await self.meeting_recorder_agent.process(
                genre=self.state.genre,
                tone=self.state.tone,
                themes=self.state.themes,
                pitch=self.state.selected_pitch,
                trope_analysis=self.state.trope_analysis,
                output_dir=self.state.output_path or self.output_dir
            )
            
            if result["status"] == "success":
                self._update_state(
                    stage=GenerationStage.COMPLETED
                )
                self.logger.info("Completed documentation")
            else:
                raise Exception(f"Documentation failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            await self._handle_error(e, GenerationStage.DOCUMENTATION)
            raise
    
    async def process(
        self,
        genre: Optional[str] = None,
        tone: Optional[str] = None,
        themes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Process the story idea generation.
        
        Args:
            genre: Optional specific genre to use
            tone: Optional specific tone to use
            themes: Optional list of themes to use
            
        Returns:
            Dict containing the generated idea data
        """
        try:
            # Initialize state
            self._update_state(stage=GenerationStage.INITIAL)
            
            # Run genre selection
            if not tone or not themes:
                await self._run_genre_selection(genre)
            else:
                self._update_state(
                    stage=GenerationStage.PITCH_GENERATION,
                    genre=genre,
                    tone=tone,
                    themes=themes
                )
            
            # Run pitch generation
            await self._run_pitch_generation()
            
            # Run critic evaluation
            await self._run_critic_evaluation()
            
            # Run pitch improvement
            await self._run_pitch_improvement()
            
            # Run pitch selection
            await self._run_pitch_selection()
            
            # Run trope analysis
            await self._run_trope_analysis()
            
            # Run documentation
            await self._run_documentation()
            
            return {
                "status": "success",
                "genre": self.state.genre,
                "tone": self.state.tone,
                "themes": self.state.themes,
                "selected_pitch": self.state.selected_pitch,
                "selection_data": self.state.selection_data,
                "trope_analysis": self.state.trope_analysis,
                "output_path": str(self.state.output_path) if self.state.output_path else None
            }
            
        except Exception as e:
            self.logger.error(f"Error in idea generation process: {e}")
            return {
                "status": "error",
                "error": str(e)
            } 