#!/bin/bash

# The PersonalGPT Project
# Version: 3.2
# This is the launch script for the PersonalGPT project.

# Clear the terminal
clear

# Output header information
echo "The PersonalGPT Project"
echo "Version: 3.2"
echo "This is the launch script for the PersonalGPT project."
echo

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the Python module
python -m src
