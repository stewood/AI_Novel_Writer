#!/usr/bin/env python
"""Test script for diagnosing PitchGeneratorAgent issues with nanopunk genre.

This script directly calls the PitchGeneratorAgent with similar parameters to what
was used in the logs, allowing us to diagnose the issue with missing pitch data.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.append(".")

from src.novelwriter_idea.agents.pitch_generator_agent import PitchGeneratorAgent
from src.novelwriter_idea.config.llm import LLMConfig
from src.novelwriter_idea.config.logging import setup_logging, SUPERDEBUG

# Configure logging
setup_logging(level=SUPERDEBUG, console=True, log_file="logs/test_pitch_generator_nanopunk.log")
logger = logging.getLogger("test_script")

async def test_pitch_generation():
    """Test the PitchGeneratorAgent with nanopunk genre parameters."""
    # Ensure we have the API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable is not set")
        print("Error: OPENROUTER_API_KEY environment variable is required")
        return 1
        
    # Create LLM config
    llm_config = LLMConfig(api_key=api_key)
    
    # Create the PitchGeneratorAgent
    agent = PitchGeneratorAgent(llm_config)
    
    # Define the same parameters seen in the logs
    genre = "science_fiction"
    subgenre = "nanopunk"
    tone = """Gritty, cynical optimism. The story should feel lived-in and worn, reflecting a world constantly patched together with temporary solutions. There's a pervasive sense of decay and corporate control, but not a hopeless one. Characters are resourceful and pragmatic, often operating in shades of grey, and while they acknowledge the bleakness, they still strive for small victories and personal connections. Think a blend of *Blade Runner*'s visual aesthetic with the weary resilience of *The Expanse*'s characters, but focused on the *very* small scale – the individual navigating the system, not galactic empires. The narration should lean towards internal monologue and observational detail, emphasizing the sensory experience of a hyper-dense, technologically saturated environment. A feeling of *precariousness* should be constant."""
    
    themes = [
        "**The Commodification of the Self:** Bodies and identities are increasingly customizable and marketable, blurring the lines between personhood and product.",
        "**Decentralization vs. Control:** The promise of nanotechnology enabling individual empowerment clashes with the reality of corporations and governments seeking to monopolize and control its use.",
        "**The Illusion of Progress:** Technological advancement doesn't necessarily equate to societal improvement; it can exacerbate existing inequalities and create new forms of oppression.",
        "**Finding Meaning in a Synthetic World:** In a reality where the natural is increasingly rare and the artificial dominates, characters struggle to define authenticity and purpose.",
        "**The Ethics of Radical Enhancement:** Exploring the moral implications of using nanotechnology to fundamentally alter human capabilities, and the potential for creating a new form of social stratification based on access to these enhancements."
    ]
    
    logger.info("Starting pitch generation test with nanopunk genre")
    print("Starting pitch generation test...")
    
    try:
        # Generate pitches
        pitches = await agent.generate_pitches(
            genre=genre,
            subgenre=subgenre,
            tone=tone,
            themes=themes
        )
        
        # Print results
        logger.info(f"Generated {len(pitches)} pitches")
        print(f"\nSuccessfully generated {len(pitches)} pitches:")
        
        for i, pitch in enumerate(pitches, 1):
            print(f"\n--- Pitch {i}: {pitch.get('title', 'Untitled')} ---")
            # Validate and print each section
            for section in ["title", "hook", "premise", "main_conflict", "unique_twist"]:
                content = pitch.get(section, "[MISSING]")
                print(f"{section.replace('_', ' ').title()}: {content}")
                # Check for missing sections
                if content == "[Missing]":
                    print(f"   ⚠️ WARNING: Missing {section}")
                    
        # Save the results to file for analysis
        with open("pitch_test_results.json", "w") as f:
            json.dump(pitches, f, indent=2)
            
        print(f"\nFull results saved to pitch_test_results.json")
        return 0
        
    except Exception as e:
        logger.error(f"Error in pitch generation: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(test_pitch_generation())
    sys.exit(exit_code) 