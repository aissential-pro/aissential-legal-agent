# AIssential Legal Agent - Bot Supervisor Launcher
# Run this script to start the bot with automatic restart capability

Write-Host "========================================"
Write-Host "AIssential Legal Agent - Bot Supervisor"
Write-Host "========================================"
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
$venvPath = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    . $venvPath
    Write-Host "Virtual environment activated"
} else {
    Write-Host "Warning: Virtual environment not found at $venvPath" -ForegroundColor Yellow
}

# Start the supervisor
Write-Host "Starting supervisor..."
python app\supervisor.py

Read-Host "Press Enter to exit"
