#!/bin/bash
echo "Activating virtual environment..."
source venv/bin/activate

echo "Running Novel Writer..."
python run_novel_writer.py "$@"

echo "Done!" 