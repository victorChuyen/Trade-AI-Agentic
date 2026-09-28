# ==============================================================================
# 🏆 OPC AI TRADER (LUCKY TRADE OS) — WINDOWS VPS 24/7 AUTO-PROVISIONING SCRIPT
# Run this script in PowerShell as Administrator on opc-trade-win-01 (34.87.156.228)
# ==============================================================================

Write-Host ">>> [1/5] Configuring Execution Policy & Package Manager..." -ForegroundColor Cyan
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

# Install Chocolatey if not present
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host ">>> Installing Chocolatey..." -ForegroundColor Yellow
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Refresh Environment
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ">>> [2/5] Installing Git and Python 3.11..." -ForegroundColor Cyan
choco install -y git python311

# Update PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ">>> [3/5] Downloading and Installing MetaTrader 5 Terminal..." -ForegroundColor Cyan
$mt5Path = "$env:TEMP\mt5setup.exe"
if (-not (Test-Path "C:\Program Files\MetaTrader 5\terminal64.exe")) {
    Invoke-WebRequest -Uri "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe" -OutFile $mt5Path
    Start-Process -FilePath $mt5Path -ArgumentList "/auto" -Wait
    Start-Sleep -Seconds 5
}
Write-Host ">>> MetaTrader 5 Installed successfully at C:\Program Files\MetaTrader 5\terminal64.exe" -ForegroundColor Green

Write-Host ">>> [4/5] Setting up Project Workspace at C:\OPC-AI-TRADER..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "C:\OPC-AI-TRADER" | Out-Null
cd "C:\OPC-AI-TRADER"

# Clone repository or initialize
if (-not (Test-Path "C:\OPC-AI-TRADER\.git")) {
    git clone https://github.com/victorChuyen/Trade-AI-Agentic.git C:\OPC-AI-TRADER
}

# Setup Python Virtual Environment
Write-Host ">>> Setting up Python 3.11 Virtual Environment..." -ForegroundColor Cyan
py -3.11 -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r service\requirements.txt

Write-Host ">>> [5/5] Launching MetaTrader 5 and OPC AI Trader Engine..." -ForegroundColor Green
Start-Process "C:\Program Files\MetaTrader 5\terminal64.exe"
Start-Sleep -Seconds 3

# Launch Backend Server
Write-Host ">>> OPC AI Trader 24/7 is now LIVE on http://localhost:8000" -ForegroundColor Green
& ".\.venv\Scripts\python.exe" service\server\main.py
