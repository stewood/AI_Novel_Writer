"""Facilitator Agent for orchestrating the idea generation workflow.

This agent coordinates the entire idea generation process, delegating tasks to
specialized agents and managing the workflow from initial input to final output.
"""

import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple

from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.agents.base_agent import BaseAgent
from novelwriter_idea.agents.genre_vibe_agent import GenreVibeAgent
from novelwriter_idea.agents.pitch_generator_agent import PitchGeneratorAgent
from novelwriter_idea.agents.critic_agent import CriticAgent
from novelwriter_idea.agents.improver_agent import ImproverAgent
from novelwriter_idea.agents.voter_agent import VoterAgent
from novelwriter_idea.agents.tropemaster_agent import TropemasterAgent
from novelwriter_idea.agents.meeting_recorder_agent import MeetingRecorderAgent

# Initialize logger
logger = logging.getLogger(__name__)

class FacilitatorAgent(BaseAgent):
    """Agent responsible for orchestrating the idea generation workflow.
    
    This agent coordinates the entire process, managing specialized agents and
    ensuring they work together effectively to generate a high-quality story idea.
    The facilitator delegates tasks, consolidates results, and makes decisions
    about workflow progression.
    """

    def __init__(self, llm_config: LLMConfig):
        """Initialize the Facilitator Agent.
        
        Args:
            llm_config: Configuration for the LLM client
        """
        super().__init__(llm_config)
        logger.info("Initializing Facilitator Agent")
        
        # Initialize specialized agents
        self.genre_vibe_agent = GenreVibeAgent(llm_config)
        self.pitch_generator_agent = PitchGeneratorAgent(llm_config)
        self.critic_agent = CriticAgent(llm_config)
        self.improver_agent = ImproverAgent(llm_config)
        self.voter_agent = VoterAgent(llm_config)
        self.tropemaster_agent = TropemasterAgent(llm_config)
        self.meeting_recorder_agent = MeetingRecorderAgent(llm_config)
        
        logger.debug("All specialized agents initialized")
        
    async def generate_idea(
        self,
        genre: Optional[str] = None,
        tone: Optional[str] = None,
        themes: Optional[List[str]] = None,
        output_dir: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Orchestrate the idea generation workflow.
        
        This method coordinates the entire process of generating a story idea,
        from determining genre and tone to creating and evaluating pitches,
        selecting the best one, analyzing tropes, and compiling the final document.
        
        Args:
            genre: Optional specific genre to use
            tone: Optional specific tone to use
            themes: Optional specific themes to incorporate
            output_dir: Optional directory for saving the output file
            
        Returns:
            Tuple containing (output_file_path, idea_data)
        """
        self._log_method_start(
            "generate_idea", 
            has_genre=genre is not None,
            has_tone=tone is not None,
            has_themes=themes is not None and len(themes) > 0,
            has_output_dir=output_dir is not None
        )
        
        logger.info("Beginning idea generation workflow")
        
        try:
            # Step 1: Determine genre, tone, and themes
            logger.info("Step 1: Determining genre, tone, and themes")
            genre_data = await self._determine_genre_tone_themes(genre, tone, themes)
            
            # Step 2: Generate story pitches
            logger.info("Step 2: Generating story pitches")
            pitches = await self._generate_story_pitches(
                genre_data["genre"],
                genre_data["subgenre"],
                genre_data["tone"],
                genre_data["themes"]
            )
            
            # Step 3: Evaluate pitches
            logger.info("Step 3: Evaluating story pitches")
            evaluations = await self._evaluate_pitches(
                pitches,
                genre_data["genre"],
                genre_data["subgenre"],
                genre_data["tone"],
                genre_data["themes"]
            )
            
            # Step 4: Improve pitches based on evaluations
            logger.info("Step 4: Improving pitches based on evaluations")
            improved_pitches = await self._improve_pitches(
                pitches,
                evaluations,
                genre_data["genre"],
                genre_data["subgenre"],
                genre_data["tone"],
                genre_data["themes"]
            )
            
            # Step 5: Select the best pitch
            logger.info("Step 5: Selecting the best pitch")
            selection_data = await self._select_best_pitch(
                improved_pitches,
                evaluations,
                genre_data["genre"],
                genre_data["subgenre"],
                genre_data["tone"],
                genre_data["themes"]
            )
            
            # Get the winner pitch
            winner_title = selection_data.get("winner", "")
            logger.info(f"Selected winner: {winner_title}")
            
            winner_pitch = None
            for pitch in improved_pitches:
                if pitch.get("title", "") == winner_title:
                    winner_pitch = pitch
                    break
                    
            if not winner_pitch:
                logger.warning(f"Could not find winner pitch with title '{winner_title}', using first pitch")
                winner_pitch = improved_pitches[0]
                
            # Step 6: Analyze tropes in the winning pitch
            logger.info("Step 6: Analyzing tropes in the winning pitch")
            trope_analysis = await self._analyze_tropes(
                winner_pitch,
                genre_data["genre"],
                genre_data["subgenre"],
                genre_data["tone"],
                genre_data["themes"]
            )
            
            # Step 7: Compile the final document
            logger.info("Step 7: Compiling the final document")
            output_path, document_content = await self._compile_idea(
                winner_pitch,
                selection_data,
                trope_analysis,
                genre_data["genre"],
                genre_data["subgenre"],
                genre_data["tone"],
                genre_data["themes"],
                output_dir
            )
            
            # Prepare result data
            idea_data = {
                "genre": genre_data["genre"],
                "subgenre": genre_data["subgenre"],
                "tone": genre_data["tone"],
                "themes": genre_data["themes"],
                "selected_pitch": winner_pitch,
                "selection_data": selection_data,
                "trope_analysis": trope_analysis
            }
            
            logger.info(f"Idea generation workflow completed successfully")
            self._log_method_end("generate_idea", result=output_path)
            return output_path, idea_data
            
        except Exception as e:
            error_msg = f"Error in idea generation workflow: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self._log_method_error("generate_idea", e)
            raise
            
    async def _determine_genre_tone_themes(
        self,
        genre: Optional[str] = None,
        tone: Optional[str] = None,
        themes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Determine the genre, subgenre, tone, and themes for the story.
        
        Args:
            genre: Optional specific genre to use
            tone: Optional specific tone to use
            themes: Optional specific themes to incorporate
            
        Returns:
            Dictionary with genre, subgenre, tone, and themes
        """
        logger.debug("Determining genre, tone, and themes")
        logger.debug(f"Input values - Genre: {genre}, Tone: {tone is not None}, Themes: {themes is not None}")
        
        # Process with the GenreVibeAgent
        genre_data = await self.genre_vibe_agent.process(
            genre=genre,
            tone=tone,
            themes=themes
        )
        
        # Log the results
        logger.info(f"Selected genre: {genre_data['genre']} - Subgenre: {genre_data['subgenre']}")
        logger.debug(f"Generated tone: {genre_data['tone'][:50]}..." if len(genre_data['tone']) > 50 else f"Generated tone: {genre_data['tone']}")
        themes_str = ', '.join(genre_data['themes'][:3]) + (f"... and {len(genre_data['themes'])-3} more" if len(genre_data['themes']) > 3 else "")
        logger.debug(f"Generated themes: {themes_str}")
        
        return genre_data
        
    async def _generate_story_pitches(
        self,
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> List[Dict[str, str]]:
        """Generate multiple story pitches.
        
        Args:
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            List of generated story pitches
        """
        logger.debug(f"Generating story pitches for {subgenre} ({genre})")
        
        # Generate pitches with the PitchGeneratorAgent
        pitches = await self.pitch_generator_agent.generate_pitches(
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Log the results
        pitch_count = len(pitches)
        logger.info(f"Generated {pitch_count} story pitches")
        
        # Log a sample of pitch titles
        if pitch_count > 0:
            titles = [pitch.get("title", f"Untitled {i+1}") for i, pitch in enumerate(pitches)]
            titles_sample = titles[:3]
            if len(titles) > 3:
                titles_sample_str = f"{', '.join(titles_sample)}... and {len(titles)-3} more"
            else:
                titles_sample_str = ', '.join(titles_sample)
            logger.debug(f"Pitch titles: {titles_sample_str}")
            
        return pitches
        
    async def _evaluate_pitches(
        self,
        pitches: List[Dict[str, str]],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> List[Dict[str, Any]]:
        """Evaluate the generated story pitches.
        
        Args:
            pitches: List of story pitches to evaluate
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            List of pitch evaluations
        """
        logger.debug(f"Evaluating {len(pitches)} story pitches")
        
        # Evaluate pitches with the CriticAgent
        evaluations = await self.critic_agent.evaluate_pitches(
            pitches=pitches,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Log the results
        evaluation_count = len(evaluations)
        logger.info(f"Completed evaluation of {evaluation_count} pitches")
        
        # Log evaluation summary
        if evaluation_count > 0:
            # Calculate average scores
            avg_scores = []
            for eval_data in evaluations:
                if "scores" in eval_data and eval_data["scores"]:
                    avg = sum(eval_data["scores"].values()) / len(eval_data["scores"])
                    avg_scores.append(avg)
                elif "overall_score" in eval_data:
                    avg_scores.append(eval_data["overall_score"])
                    
            if avg_scores:
                overall_avg = sum(avg_scores) / len(avg_scores)
                max_score = max(avg_scores)
                min_score = min(avg_scores)
                logger.debug(f"Evaluation scores - Avg: {overall_avg:.1f}, Max: {max_score:.1f}, Min: {min_score:.1f}")
                
        return evaluations
        
    async def _improve_pitches(
        self,
        pitches: List[Dict[str, str]],
        evaluations: List[Dict[str, Any]],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> List[Dict[str, str]]:
        """Improve pitches based on evaluation feedback.
        
        Args:
            pitches: List of story pitches
            evaluations: List of pitch evaluations
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            List of improved pitches
        """
        logger.debug(f"Improving {len(pitches)} story pitches based on evaluations")
        
        improved_pitches = []
        threshold_score = 7.5  # Only improve pitches with scores below this threshold
        
        # Process each pitch
        for i, (pitch, evaluation) in enumerate(zip(pitches, evaluations)):
            pitch_title = pitch.get("title", f"Pitch {i+1}")
            logger.debug(f"Processing pitch {i+1}: {pitch_title}")
            
            # Calculate average score
            avg_score = 0
            if "overall_score" in evaluation:
                avg_score = evaluation["overall_score"]
            elif "scores" in evaluation:
                scores = evaluation["scores"]
                if scores:
                    avg_score = sum(scores.values()) / len(scores)
                    
            logger.debug(f"Pitch '{pitch_title}' has score: {avg_score:.1f}")
            
            # Decide whether to improve the pitch
            if avg_score < threshold_score:
                logger.info(f"Improving pitch '{pitch_title}' (score: {avg_score:.1f})")
                
                # Improve pitch with the ImproverAgent
                improved_pitch = await self.improver_agent.improve_pitch(
                    pitch=pitch,
                    evaluation=evaluation,
                    genre=genre,
                    subgenre=subgenre,
                    tone=tone,
                    themes=themes
                )
                
                improved_pitches.append(improved_pitch)
                logger.debug(f"Successfully improved pitch '{pitch_title}'")
            else:
                logger.debug(f"Pitch '{pitch_title}' already meets quality threshold (score: {avg_score:.1f})")
                improved_pitches.append(pitch)
                
        logger.info(f"Improvement process completed for {len(pitches)} pitches")
        return improved_pitches
        
    async def _select_best_pitch(
        self,
        pitches: List[Dict[str, str]],
        evaluations: List[Dict[str, Any]],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> Dict[str, Any]:
        """Select the best pitch from the improved options.
        
        Args:
            pitches: List of story pitches
            evaluations: List of pitch evaluations
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            Selection data including winner and rationale
        """
        logger.debug(f"Selecting the best pitch from {len(pitches)} options")
        
        # Select the best pitch with the VoterAgent
        selection_data = await self.voter_agent.select_best_pitch(
            pitches=pitches,
            evaluations=evaluations,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Log the results
        winner = selection_data.get("winner", "Unknown")
        logger.info(f"Selected best pitch: '{winner}'")
        
        # Log selection criteria
        if "selection_criteria" in selection_data and selection_data["selection_criteria"]:
            criteria_count = len(selection_data["selection_criteria"])
            logger.debug(f"Selection based on {criteria_count} criteria")
            for i, criterion in enumerate(selection_data["selection_criteria"][:2], 1):
                logger.debug(f"Criterion {i}: {criterion[:80]}...")
            if criteria_count > 2:
                logger.debug(f"...and {criteria_count - 2} more criteria")
                
        return selection_data
        
    async def _analyze_tropes(
        self,
        pitch: Dict[str, str],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str]
    ) -> Dict[str, Any]:
        """Analyze tropes in the selected pitch and suggest improvements.
        
        Args:
            pitch: The selected story pitch
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            
        Returns:
            Trope analysis data
        """
        logger.debug(f"Analyzing tropes in selected pitch: '{pitch.get('title', 'Untitled')}'")
        
        # Analyze tropes with the TropemasterAgent
        trope_analysis = await self.tropemaster_agent.analyze_tropes(
            pitch=pitch,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Log the results
        trope_count = len(trope_analysis.get("identified_tropes", []))
        logger.info(f"Identified {trope_count} tropes in the selected pitch")
        
        # Log a sample of identified tropes
        if trope_count > 0:
            tropes = trope_analysis.get("identified_tropes", [])
            for i, trope in enumerate(tropes[:2], 1):
                logger.debug(f"Trope {i}: {trope.get('name', 'Unnamed')} - {trope.get('overuse_level', 'Unknown')} overuse")
            if trope_count > 2:
                logger.debug(f"...and {trope_count - 2} more tropes")
                
        # Log alternative count
        alt_count = 0
        if "suggested_alternatives" in trope_analysis:
            for trope_name, alternatives in trope_analysis["suggested_alternatives"].items():
                alt_count += len(alternatives)
        logger.debug(f"Generated {alt_count} alternative suggestions for tropes")
        
        return trope_analysis
        
    async def _compile_idea(
        self,
        pitch: Dict[str, str],
        selection_data: Dict[str, Any],
        trope_analysis: Dict[str, Any],
        genre: str,
        subgenre: str,
        tone: str,
        themes: List[str],
        output_dir: Optional[str] = None
    ) -> Tuple[str, str]:
        """Compile the final idea document.
        
        Args:
            pitch: The selected story pitch
            selection_data: Selection rationale and recommendations
            trope_analysis: Analysis of tropes and suggested alternatives
            genre: The main genre category
            subgenre: The specific subgenre
            tone: The desired tone for the story
            themes: List of themes to incorporate
            output_dir: Optional directory for saving the output file
            
        Returns:
            Tuple containing (file_path, document_content)
        """
        logger.debug(f"Compiling final idea document for pitch: '{pitch.get('title', 'Untitled')}'")
        
        # Compile idea with the MeetingRecorderAgent
        file_path, document_content = await self.meeting_recorder_agent.compile_idea(
            selected_pitch=pitch,
            selection_data=selection_data,
            trope_analysis=trope_analysis,
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes,
            output_dir=output_dir
        )
        
        # Log the results
        logger.info(f"Final idea document compiled and saved to: {file_path}")
        logger.debug(f"Document length: {len(document_content)} characters")
        
        return file_path, document_content 