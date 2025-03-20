@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Running Novel Writer...
python run_novel_writer.py %*

echo Done! 