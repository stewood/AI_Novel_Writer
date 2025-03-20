"""Test configuration for pytest."""
import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent

# Add the src directory to the Python path
src_path = os.path.join(project_root, "src")
sys.path.append(str(src_path)) 