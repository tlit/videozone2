$ErrorActionPreference = "Stop"

Write-Host "Starting VideoZone..." -ForeColor Cyan

$Root = Get-Location
$BackendDir = Join-Path $Root "backend"
$VenvDir = Join-Path $BackendDir "venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$Requirements = Join-Path $BackendDir "requirements.txt"
$BasePython = "C:\Python312\python.exe"

# 1. Check/Create Virtual Environment
if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual environment not found. Creating..." -ForeColor Yellow
    if (-not (Test-Path $BasePython)) {
        throw "Python 3.12 not found at $BasePython. Please install Python 3.12 or update the script."
    }
    Start-Process -FilePath $BasePython -ArgumentList "-m venv $VenvDir" -Wait -NoNewWindow
    
    Write-Host "Installing dependencies..." -ForeColor Yellow
    $Pip = Join-Path $VenvDir "Scripts\pip.exe"
    Start-Process -FilePath $Pip -ArgumentList "install -r $Requirements" -Wait -NoNewWindow
}

# 2. Start Backend
Write-Host "Launching Backend (FastAPI)..." -ForeColor Green
$BackendCmd = "$VenvPython -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& { cd $Root; $BackendCmd }"

# 3. Start Frontend
Write-Host "Launching Frontend (Vite)..." -ForeColor Magenta
$FrontendDir = Join-Path $Root "frontend"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& { cd $FrontendDir; npm install; npm run dev }"

Write-Host "VideoZone is initializing..." -ForeColor Cyan
Write-Host "Backend: http://localhost:8000" -ForeColor Gray
Write-Host "Frontend: http://localhost:5173" -ForeColor Yellow

