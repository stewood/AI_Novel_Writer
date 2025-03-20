#!/bin/bash

echo "==================================================="
echo "Novel Writer - Installation Script"
echo "==================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in the PATH."
    echo "Please install Python 3.8 or later and try again."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment and install requirements
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Upgrade pip
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "Warning: Failed to upgrade pip. Continuing anyway..."
fi

# Install required packages
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements."
    exit 1
fi

# Install the package in development mode
pip install -e .
if [ $? -ne 0 ]; then
    echo "Error: Failed to install the package in development mode."
    exit 1
fi

# Install python-dotenv if not already installed
pip install python-dotenv
if [ $? -ne 0 ]; then
    echo "Error: Failed to install python-dotenv."
    exit 1
fi

# Check if .env file exists, create template if not
if [ ! -f ".env" ]; then
    echo "Creating template .env file..."
    cat > .env << EOL
# OpenRouter API Keys
# Paid API key
OPENROUTER_API_KEY=your_paid_key_here
# Free API key
OPENROUTER_FREE_API_KEY=your_free_key_here
EOL
    echo ""
    echo "Please edit the .env file and add your API keys."
fi

# Make the run script executable
chmod +x run_novel_writer.py

echo ""
echo "==================================================="
echo "Installation complete!"
echo ""
echo "To run the novel writer:"
echo "  1. Ensure your API keys are in the .env file"
echo "  2. Run: python run_novel_writer.py"
echo ""
echo "For help with available options:"
echo "  python run_novel_writer.py --help"
echo "===================================================" 