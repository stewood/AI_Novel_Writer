#!/usr/bin/env python
"""
Novel Writer Runner

This script runs the novel_writer tool with the specified settings,
loading API keys from the .env file.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the novel_writer tool with keys from .env file"
    )
    parser.add_argument(
        "--log-level",
        choices=["ERROR", "WARN", "INFO", "DEBUG", "SUPERDEBUG"],
        default="SUPERDEBUG",
        help="Set the logging level (default: SUPERDEBUG)"
    )
    parser.add_argument(
        "--genre",
        help="Specify a genre for the story"
    )
    parser.add_argument(
        "--tone",
        help="Specify the emotional/narrative tone"
    )
    parser.add_argument(
        "--themes",
        nargs="+",
        help="Specify themes to explore"
    )
    parser.add_argument(
        "--output",
        help="Path for the output file"
    )
    
    return parser.parse_args()

def main():
    """Run the novel_writer tool with API keys from .env file."""
    args = parse_args()
    print("Running novel_writer with API keys from .env file...")
    
    # Ensure the .env file exists
    env_path = Path(".env")
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path.absolute()}")
        print("Please create a .env file with your API keys.")
        return 1
        
    # Build the command
    cmd = [
        sys.executable,
        "src/novel_writer/cli.py",
        "--log-level", args.log_level,
        "idea"
    ]
    
    # Add optional arguments if provided
    if args.genre:
        cmd.extend(["--genre", args.genre])
    
    if args.tone:
        cmd.extend(["--tone", args.tone])
    
    if args.themes:
        cmd.extend(["--themes"])
        cmd.extend(args.themes)
    
    if args.output:
        cmd.extend(["--output", args.output])
    
    # Run the command
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running novel_writer: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 