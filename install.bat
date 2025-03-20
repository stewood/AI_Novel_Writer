@echo off
echo ===================================================
echo Novel Writer - Installation Script
echo ===================================================

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in the PATH.
    echo Please install Python 3.8 or later and try again.
    exit /b 1
)

:: Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
)

:: Activate virtual environment and install requirements
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to activate virtual environment.
    exit /b 1
)

:: Upgrade pip
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to upgrade pip. Continuing anyway...
)

:: Install required packages
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install requirements.
    exit /b 1
)

:: Install the package in development mode
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install the package in development mode.
    exit /b 1
)

:: Install python-dotenv if not already installed
pip install python-dotenv
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install python-dotenv.
    exit /b 1
)

:: Check if .env file exists, create template if not
if not exist .env (
    echo Creating template .env file...
    echo # OpenRouter API Keys > .env
    echo # Paid API key >> .env
    echo OPENROUTER_API_KEY=your_paid_key_here >> .env
    echo # Free API key >> .env
    echo OPENROUTER_FREE_API_KEY=your_free_key_here >> .env
    echo.
    echo Please edit the .env file and add your API keys.
)

echo.
echo ===================================================
echo Installation complete!
echo.
echo To run the novel writer:
echo   1. Ensure your API keys are in the .env file
echo   2. Run: python run_novel_writer.py
echo.
echo For help with available options:
echo   python run_novel_writer.py --help
echo =================================================== 