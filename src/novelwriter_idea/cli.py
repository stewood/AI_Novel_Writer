"""Command-line interface for the novelwriter_idea tool.

This module provides the main CLI entry point for the novelwriter_idea tool,
including argument parsing, command routing, and execution of the appropriate
workflows based on user input.
"""

import argparse
import asyncio
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

from novelwriter_idea.agents.facilitator_agent import FacilitatorAgent
from novelwriter_idea.config.llm import LLMConfig
from novelwriter_idea.config.logging import setup_logging, SUPERDEBUG

# Initialize logger
logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Sets up the main parser and subparsers for different commands,
    along with their respective arguments and flags.
    
    Returns:
        Configured argument parser
    """
    logger.debug("Creating argument parser")
    
    parser = argparse.ArgumentParser(
        prog="novelwriter_idea",
        description="AI-powered novel idea generator and outlining tool"
    )
    
    # Global arguments
    parser.add_argument(
        "--log-level",
        choices=["ERROR", "WARN", "INFO", "DEBUG", "SUPERDEBUG"],
        default="INFO",
        help="Set the logging level"
    )
    
    parser.add_argument(
        "--log-file",
        default=None,
        help="Path to the log file (defaults to logs/novelwriter_TIMESTAMP.log if not specified)"
    )
    
    parser.add_argument(
        "--console-log",
        action="store_true",
        help="Enable detailed logging to console (status updates are always shown regardless of this setting)"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Idea generation command
    idea_parser = subparsers.add_parser("idea", help="Generate a novel idea")
    idea_parser.add_argument("--genre", help="Specify a genre for the story")
    idea_parser.add_argument("--tone", help="Specify the emotional/narrative tone")
    idea_parser.add_argument("--themes", nargs="+", help="Specify themes to explore")
    idea_parser.add_argument("--output", help="Path for the output file")
    
    # Future commands can be added here
    # outline_parser = subparsers.add_parser("outline", help="Generate a story outline")
    # scene_parser = subparsers.add_parser("scene", help="Generate a scene description")
    
    logger.debug("Argument parser created with subcommands: idea")
    return parser

def print_status(message: str, emoji: str = "📝") -> None:
    """Print a status message to the console regardless of console logging setting.
    
    Args:
        message: The message to print
        emoji: Optional emoji to include at the start of the message
    """
    if emoji:
        print(f"\n{emoji} {message}")
    else:
        print(f"\n{message}")
    
    # Also log this message at INFO level
    logger.info(message)

def setup_llm_config() -> LLMConfig:
    """Set up the LLM configuration.
    
    Retrieves API keys from environment variables and initializes
    the LLM configuration with appropriate settings.
    
    Returns:
        Configured LLM client
    
    Raises:
        EnvironmentError: If required API keys are missing
    """
    logger.debug("Setting up LLM configuration")
    
    # Get API key from environment variable
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        error_msg = "OPENROUTER_API_KEY environment variable not set"
        logger.error(error_msg)
        raise EnvironmentError(
            "OPENROUTER_API_KEY environment variable is required. "
            "Please set it to your OpenRouter API key."
        )
    
    logger.debug("Found OPENROUTER_API_KEY in environment variables")
    
    # Initialize LLM configuration
    llm_config = LLMConfig(api_key=api_key)
    logger.info("LLM configuration initialized successfully")
    logger.superdebug(f"LLM config: {llm_config.__dict__}")
    return llm_config

async def run_idea_command(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the idea generation command.
    
    Initializes the Facilitator Agent and orchestrates the idea generation
    workflow based on the provided command line arguments.
    
    Args:
        args: Command line arguments namespace
        
    Returns:
        Dictionary containing the result of the idea generation process
    """
    logger.info("Starting idea generation command")
    logger.debug(f"Command arguments: {args}")
    
    # Print welcome message
    print_status("Starting AI Novel Idea Generator...", "🚀")
    
    # Setup LLM configuration
    print_status("Setting up AI configuration...", "⚙️")
    try:
        llm_config = setup_llm_config()
        logger.debug("LLM configuration setup completed")
    except Exception as e:
        error_msg = f"Failed to set up LLM configuration: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print_status(f"Error: {error_msg}", "❌")
        return {"status": "error", "error": error_msg}
    
    # Initialize facilitator agent
    try:
        facilitator = FacilitatorAgent(llm_config)
        logger.debug("Facilitator agent initialized")
    except Exception as e:
        error_msg = f"Failed to initialize Facilitator Agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print_status(f"Error: {error_msg}", "❌")
        return {"status": "error", "error": error_msg}
    
    # Convert themes from string list to list if provided
    themes = args.themes if args.themes else None
    logger.debug(f"Themes argument: {themes}")
    
    # Get output path if provided
    output_path = args.output if args.output else None
    if output_path:
        logger.debug(f"Using specified output path: {output_path}")
    else:
        logger.debug("No output path specified, will use default")
    
    # Print input parameters
    if args.genre:
        print_status(f"Using specified genre: {args.genre}", "📚")
        logger.info(f"Using specified genre: {args.genre}")
    else:
        print_status("Selecting a random genre...", "📚")
        logger.info("No genre specified, will select randomly")
        
    if args.tone:
        print_status(f"Using specified tone: {args.tone}", "🎭")
        logger.info(f"Using specified tone: {args.tone}")
    else:
        print_status("Generating appropriate tone...", "🎭")
        logger.info("No tone specified, will generate automatically")
        
    if themes:
        themes_str = ', '.join(themes)
        print_status(f"Using specified themes: {themes_str}", "💡")
        logger.info(f"Using specified themes: {themes_str}")
    else:
        print_status("Generating story themes...", "💡")
        logger.info("No themes specified, will generate automatically")
    
    print_status("Starting the idea generation process...", "📝")
    
    # Create progress tracker
    logger.debug("Creating progress tracker")
    progress_tracker = _create_progress_tracker()
    
    # Generate idea with progress updates
    try:
        logger.info("Starting idea generation with progress tracking")
        result = await _generate_idea_with_progress(
            facilitator=facilitator,
            genre=args.genre,
            tone=args.tone,
            themes=themes,
            output_path=output_path,
            progress_tracker=progress_tracker
        )
        
        logger.info("Idea generation process completed")
        logger.debug(f"Idea generation result status: {result.get('status', 'unknown')}")
        
        return result
        
    except Exception as e:
        error_msg = f"Idea generation failed: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print_status(f"Error: {error_msg}", "❌")
        return {"status": "error", "error": error_msg}

def _create_progress_tracker() -> Callable[[int], None]:
    """Create a function that tracks and displays progress.
    
    Returns:
        A function that takes a step index and displays progress
    """
    logger.debug("Creating progress tracker function")
    
    steps = [
        "Selecting genre and tone",
        "Generating story pitches",
        "Evaluating story pitches",
        "Improving promising concepts",
        "Selecting the best pitch",
        "Analyzing story tropes",
        "Compiling final document"
    ]
    
    total_steps = len(steps)
    logger.debug(f"Progress tracker created with {total_steps} steps")
    
    def update_progress(step_index: int) -> None:
        """Update and display progress for the current step.
        
        Args:
            step_index: Index of the current step in the process
        """
        step = steps[step_index]
        progress = f"[{step_index + 1}/{total_steps}]"
        print(f"{progress} {step}...")
        logger.info(f"Progress: {progress} {step}")
    
    return update_progress

async def _generate_idea_with_progress(
    facilitator: FacilitatorAgent,
    genre: Optional[str],
    tone: Optional[str],
    themes: Optional[List[str]],
    output_path: Optional[str],
    progress_tracker: Callable[[int], None]
) -> Dict[str, Any]:
    """Generate a story idea with progress updates.
    
    Executes the idea generation workflow step by step, providing
    progress updates to the user and handling errors gracefully.
    
    Args:
        facilitator: The Facilitator Agent instance
        genre: Optional specific genre to use
        tone: Optional specific tone to use
        themes: Optional specific themes to incorporate
        output_path: Optional path for saving the output file
        progress_tracker: Function to update progress display
        
    Returns:
        Dictionary with the result of the idea generation process
    """
    logger.debug("Starting idea generation with progress tracking")
    
    result = {
        "status": "success",
        "output_path": None,
        "data": {}
    }
    
    try:
        # Step 1: Determine genre, tone, and themes
        logger.info("STEP 1: Determining genre, tone, and themes")
        progress_tracker(0)
        
        try:
            genre_info = await facilitator.genre_vibe_agent.process(
                genre=genre,
                tone=tone,
                themes=themes
            )
            
            logger.debug(f"Genre selection result: {genre_info.keys()}")
            
            if genre_info.get("status") != "success":
                error_msg = genre_info.get("error", "Unknown error in genre selection")
                logger.error(f"Genre selection failed: {error_msg}")
                print_status(f"Error: {error_msg}", "❌")
                return {"status": "error", "error": error_msg}
            
            selected_genre = genre_info["genre"]
            selected_subgenre = genre_info["subgenre"]
            selected_tone = genre_info["tone"]
            selected_themes = genre_info["themes"]
            
            logger.info(f"Selected genre: {selected_genre}, subgenre: {selected_subgenre}")
            logger.debug(f"Selected tone: {selected_tone[:100]}...")
            logger.debug(f"Selected themes: {selected_themes}")
            
            print_status(f"Selected {selected_subgenre} (a type of {selected_genre})", "✅")
            print(f"✅ Tone: {selected_tone[:60]}..." if len(selected_tone) > 60 else f"✅ Tone: {selected_tone}")
            print(f"✅ Themes: {', '.join(t[:30] for t in selected_themes[:3])}" + 
                (f" and {len(selected_themes) - 3} more..." if len(selected_themes) > 3 else ""))
            
        except Exception as e:
            error_msg = f"Failed to determine genre and tone: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print_status(f"Error: {error_msg}", "❌")
            return {"status": "error", "error": error_msg}
        
        # Step 2: Generate multiple story pitches
        logger.info("STEP 2: Generating story pitches")
        progress_tracker(1)
        
        try:
            pitches = await facilitator.pitch_generator_agent.generate_pitches(
                genre=selected_genre,
                subgenre=selected_subgenre,
                tone=selected_tone,
                themes=selected_themes
            )
            
            logger.info(f"Generated {len(pitches)} story pitches")
            logger.debug(f"Pitch titles: {[p.get('title', 'Untitled') for p in pitches]}")
            
            print_status(f"Generated {len(pitches)} story pitches:", "✅")
            for i, pitch in enumerate(pitches):
                print(f"   {i+1}. {pitch.get('title', 'Untitled')}")
                
        except Exception as e:
            error_msg = f"Failed to generate pitches: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print_status(f"Error: {error_msg}", "❌")
            return {"status": "error", "error": error_msg}
        
        # Step 3: Evaluate the pitches
        logger.info("STEP 3: Evaluating story pitches")
        progress_tracker(2)
        
        try:
            evaluations = await facilitator.critic_agent.evaluate_pitches(
                pitches=pitches,
                genre=selected_genre,
                subgenre=selected_subgenre,
                tone=selected_tone,
                themes=selected_themes
            )
            
            logger.info(f"Completed evaluation of {len(evaluations)} pitches")
            
            # Log some evaluation details
            for i, (pitch, eval_data) in enumerate(zip(pitches, evaluations)):
                title = pitch.get("title", f"Pitch {i+1}")
                strengths_count = len(eval_data.get("key_strengths", []))
                improvements_count = len(eval_data.get("areas_for_improvement", []))
                
                if "scores" in eval_data and eval_data["scores"]:
                    avg_score = sum(eval_data["scores"].values()) / len(eval_data["scores"])
                elif "overall_score" in eval_data:
                    avg_score = eval_data["overall_score"]
                else:
                    avg_score = "N/A"
                    
                logger.debug(f"Evaluation for '{title}': Score={avg_score}, " +
                             f"Strengths={strengths_count}, Improvements={improvements_count}")
            
            print_status(f"Evaluated all pitches", "✅")
            print(f"   Found strengths and areas for improvement in each concept")
            
        except Exception as e:
            error_msg = f"Failed to evaluate pitches: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print_status(f"Error: {error_msg}", "❌")
            return {"status": "error", "error": error_msg}
        
        # Step 4: Improve pitches based on evaluations
        logger.info("STEP 4: Improving pitches based on evaluations")
        progress_tracker(3)
        
        try:
            improved_pitches = []
            threshold_score = 7.5  # Only improve pitches with scores below this threshold
            
            for i, (pitch, evaluation) in enumerate(zip(pitches, evaluations)):
                title = pitch.get("title", f"Pitch {i+1}")
                
                # Calculate average score
                if "overall_score" in evaluation:
                    avg_score = evaluation["overall_score"]
                elif "scores" in evaluation and evaluation["scores"]:
                    avg_score = sum(evaluation["scores"].values()) / len(evaluation["scores"])
                else:
                    avg_score = 0
                    
                logger.debug(f"Pitch '{title}' has score: {avg_score}")
                
                # Decide whether to improve the pitch
                if avg_score < threshold_score:
                    logger.info(f"Improving pitch '{title}' (score: {avg_score})")
                    print(f"   Improving: {title}")
                    
                    improved_pitch = await facilitator.improver_agent.improve_pitch(
                        pitch=pitch,
                        evaluation=evaluation,
                        genre=selected_genre,
                        subgenre=selected_subgenre,
                        tone=selected_tone,
                        themes=selected_themes
                    )
                    
                    improved_pitches.append(improved_pitch)
                    logger.debug(f"Successfully improved pitch '{title}'")
                else:
                    logger.debug(f"Pitch '{title}' already meets quality threshold (score: {avg_score})")
                    improved_pitches.append(pitch)
            
            improved_count = sum(1 for p, ip in zip(pitches, improved_pitches) if p != ip)
            logger.info(f"Improved {improved_count} out of {len(pitches)} pitches")
            
            print_status(f"Enhanced {improved_count} pitches with targeted improvements", "✅")
                
        except Exception as e:
            error_msg = f"Failed to improve pitches: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print_status(f"Error: {error_msg}", "❌")
            return {"status": "error", "error": error_msg}
        
        # Step 5: Select the best pitch
        logger.info("STEP 5: Selecting the best pitch")
        progress_tracker(4)
        
        try:
            selection_data = await facilitator.voter_agent.select_best_pitch(
                pitches=improved_pitches,
                evaluations=evaluations,
                genre=selected_genre,
                subgenre=selected_subgenre,
                tone=selected_tone,
                themes=selected_themes
            )
            
            winner_title = selection_data.get("winner", "Unknown")
            logger.info(f"Selected best pitch: '{winner_title}'")
            
            # Find the winner pitch
            winner_pitch = None
            for pitch in improved_pitches:
                if pitch.get("title", "") == winner_title:
                    winner_pitch = pitch
                    break
                    
            if not winner_pitch:
                logger.warning(f"Could not find winner pitch with title '{winner_title}', using first pitch")
                winner_pitch = improved_pitches[0]
                winner_title = winner_pitch.get("title", "Untitled")
                
            print_status(f"Selected best pitch: '{winner_title}'", "✅")
            
            # Print some selection criteria if available
            if "selection_criteria" in selection_data and selection_data["selection_criteria"]:
                print("   Selection based on:")
                for i, criterion in enumerate(selection_data["selection_criteria"][:2], 1):
                    print(f"   - {criterion[:80]}...")
                if len(selection_data["selection_criteria"]) > 2:
                    print(f"   - ...and {len(selection_data['selection_criteria']) - 2} more criteria")
                
        except Exception as e:
            error_msg = f"Failed to select best pitch: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print_status(f"Error: {error_msg}", "❌")
            return {"status": "error", "error": error_msg}
        
        # Step 6: Analyze tropes in the winning pitch
        logger.info("STEP 6: Analyzing tropes in the winning pitch")
        progress_tracker(5)
        
        try:
            trope_analysis = await facilitator.tropemaster_agent.analyze_tropes(
                pitch=winner_pitch,
                genre=selected_genre,
                subgenre=selected_subgenre,
                tone=selected_tone,
                themes=selected_themes
            )
            
            trope_count = len(trope_analysis.get("identified_tropes", []))
            logger.info(f"Identified {trope_count} tropes in the selected pitch")
            
            # Count alternatives
            alt_count = 0
            if "suggested_alternatives" in trope_analysis:
                for trope_name, alternatives in trope_analysis["suggested_alternatives"].items():
                    alt_count += len(alternatives)
                    
            logger.debug(f"Generated {alt_count} alternative suggestions")
            
            print_status(f"Analyzed {trope_count} tropes in the story", "✅")
            print(f"   Generated {alt_count} creative alternatives to enhance originality")
                
        except Exception as e:
            error_msg = f"Failed to analyze tropes: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print_status(f"Error: {error_msg}", "❌")
            return {"status": "error", "error": error_msg}
        
        # Step 7: Compile the final document
        logger.info("STEP 7: Compiling the final document")
        progress_tracker(6)
        
        try:
            file_path, document_content = await facilitator.meeting_recorder_agent.compile_idea(
                selected_pitch=winner_pitch,
                selection_data=selection_data,
                trope_analysis=trope_analysis,
                genre=selected_genre,
                subgenre=selected_subgenre,
                tone=selected_tone,
                themes=selected_themes,
                output_dir=output_path
            )
            
            logger.info(f"Final document saved to: {file_path}")
            logger.debug(f"Document length: {len(document_content)} characters")
            
            print_status(f"Final document compiled successfully!", "✅")
            print(f"\n📁 Saved to: {file_path}")
            print(f"\n🎉 Done! Your story idea is ready for development.")
            
            # Store results
            result["output_path"] = file_path
            result["data"] = {
                "genre": selected_genre,
                "subgenre": selected_subgenre,
                "tone": selected_tone,
                "themes": selected_themes,
                "selected_pitch": winner_pitch,
                "selection_data": selection_data,
                "trope_analysis": trope_analysis
            }
                
        except Exception as e:
            error_msg = f"Failed to compile final document: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print_status(f"Error: {error_msg}", "❌")
            return {"status": "error", "error": error_msg}
            
        return result
            
    except Exception as e:
        error_msg = f"Unexpected error in idea generation: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print_status(f"Error: {error_msg}", "❌")
        return {"status": "error", "error": error_msg}

def main():
    """Main entry point for the CLI.
    
    Parses command line arguments, sets up logging, and routes
    to the appropriate command handler.
    """
    logger.debug("Parsing command line arguments")
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    logger.debug("Setting up logging configuration")
    
    log_level_name = args.log_level
    log_level = getattr(logging, log_level_name, logging.INFO)
    if log_level_name == "SUPERDEBUG":
        log_level = SUPERDEBUG
        
    setup_logging(
        log_file=args.log_file,
        level=log_level,
        console=args.console_log
    )
    
    # Display startup information
    logger.info(f"Novelwriter idea CLI started")
    logger.info(f"Command: {args.command or 'None'}")
    logger.superdebug(f"Arguments: {args}")
    
    try:
        # Route to appropriate command
        if args.command == "idea":
            # Run the idea command
            result = asyncio.run(run_idea_command(args))
            
            # Check for errors
            if result.get("status") == "error":
                logger.error(f"Idea command failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
                
            logger.info("Idea command completed successfully")
            sys.exit(0)
            
        elif args.command is None:
            logger.error("No command specified")
            parser.print_help()
            sys.exit(1)
            
        else:
            logger.error(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Command interrupted by user")
        print("\n\n⚠️  Command interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 