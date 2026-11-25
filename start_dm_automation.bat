@echo off
REM Quick Start Script for LinkedIn DM Automation
REM This script installs dependencies and starts the CLI

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   LinkedIn DM Automation - Quick Start                            ║
echo ║   Sequential Outreach for clstr.in Campus Ambassadors             ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

REM Check if venv exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    echo.
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements_dm_automation.txt

REM Start CLI
echo.
echo Starting LinkedIn DM Automation CLI...
echo.
python linkedin_dm_cli.py

pause
