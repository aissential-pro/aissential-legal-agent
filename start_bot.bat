@echo off
echo ========================================
echo AIssential Legal Agent - Bot Supervisor
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the supervisor (which manages the bot)
echo Starting supervisor...
python app\supervisor.py

pause
