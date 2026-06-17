Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Starting All-In-One ML Platform Setup Automation" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Step 1: Install Python 3.12 via Windows Package Manager
Write-Host "`n[1/4] Checking/Installing Python 3.12..." -ForegroundColor Yellow
winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements

# Step 2: Create a local virtual environment using Python 3.12
Write-Host "`n[2/4] Creating isolated Python 3.12 environment workspace..." -ForegroundColor Yellow
# Using the Windows Python Launcher to force 3.12 architecture execution
py -3.12 -m venv venv

if (-not (Test-Path ".\venv")) {
    Write-Host "ERROR: Failed to create virtual environment. Please restart VS Code and run again." -ForegroundColor Red
    Exit
}

# Step 3: Activate the virtual environment sandbox configuration 
Write-Host "`n[3/4] Activating environment..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1

# Step 4: Install the compatible production wheels for Python 3.12 environment target
Write-Host "`n[4/4] Upgrading pip and installing MediaPipe dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install opencv-python mediapipe numpy

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "SETUP SUCCESSFUL! Environment is fully configured." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "To execute your tracking application engine now, type:" -ForegroundColor White
Write-Host "python analyzer.py" -ForegroundColor Cyan