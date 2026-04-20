@echo off
REM Launcher for grunt_to_NMT.py with automatic venv activation

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Activate virtual environment
call venv_geo\Scripts\activate.bat

REM Run the script
python grunt_to_NMT.py %*

pause
