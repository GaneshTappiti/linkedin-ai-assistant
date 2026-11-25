#!/bin/bash
# Quick Start Script for LinkedIn DM Automation (macOS/Linux)

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║   LinkedIn DM Automation - Quick Start                            ║"
echo "║   Sequential Outreach for clstr.in Campus Ambassadors             ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Create venv if doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo ""
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements_dm_automation.txt

# Start CLI
echo ""
echo "Starting LinkedIn DM Automation CLI..."
echo ""
python3 linkedin_dm_cli.py
