# AIssential Legal Agent - Windows Task Scheduler Installation
# Run this script as Administrator to install the bot as a scheduled task

$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host "AIssential Legal Agent - Service Setup"
Write-Host "========================================"
Write-Host ""

# Configuration
$TaskName = "AIssential-Legal-Agent"
$TaskDescription = "AIssential Legal Agent Telegram Bot with automatic restart"
$ProjectPath = $PSScriptRoot
$PythonPath = Join-Path $ProjectPath "venv\Scripts\python.exe"
$ScriptPath = Join-Path $ProjectPath "app\supervisor.py"

# Check if running as admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "This script requires Administrator privileges." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$TaskName' already exists." -ForegroundColor Yellow
    $choice = Read-Host "Do you want to (R)eplace, (S)top, (D)elete, or (C)ancel? [R/S/D/C]"

    switch ($choice.ToUpper()) {
        "R" {
            Write-Host "Removing existing task..."
            Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }
        "S" {
            Write-Host "Stopping task..."
            Stop-ScheduledTask -TaskName $TaskName
            Write-Host "Task stopped." -ForegroundColor Green
            exit 0
        }
        "D" {
            Write-Host "Deleting task..."
            Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Host "Task deleted." -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host "Cancelled."
            exit 0
        }
    }
}

# Create the scheduled task action
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory (Join-Path $ProjectPath "app")

# Create trigger - at startup with delay
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Trigger.Delay = "PT30S"  # 30 second delay after startup

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -RestartCount 3 `
    -ExecutionTimeLimit (New-TimeSpan -Days 365)

# Register the task
Write-Host "Creating scheduled task '$TaskName'..."

try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description $TaskDescription `
        -RunLevel Highest `
        -User "SYSTEM" | Out-Null

    Write-Host ""
    Write-Host "Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The bot will:"
    Write-Host "  - Start automatically when Windows starts"
    Write-Host "  - Restart automatically if it crashes"
    Write-Host "  - Send Telegram notifications on crash/recovery"
    Write-Host ""

    # Ask to start now
    $startNow = Read-Host "Start the bot now? [Y/N]"
    if ($startNow.ToUpper() -eq "Y") {
        Write-Host "Starting task..."
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "Bot started!" -ForegroundColor Green
    }

} catch {
    Write-Host "Failed to create task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  Start:  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Stop:   Stop-ScheduledTask -TaskName '$TaskName'"
Write-Host "  Status: Get-ScheduledTask -TaskName '$TaskName' | Select-Object State"
Write-Host "  Delete: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
