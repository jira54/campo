@echo off
REM Daily Auto-Commit Script for GitHub Green Graph
REM This batch file runs the Python auto-commit script

echo 🚀 Starting daily GitHub auto-commit...
echo.

REM Change to your projects directory or run from specific paths
cd /d "d:\campo"

REM Run the Python script
python auto_commit_daily.py

echo.
echo ✅ Auto-commit completed!
echo.
pause
