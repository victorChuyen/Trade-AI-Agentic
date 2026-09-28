# ==============================================================================
# 🏆 OPC AI TRADER (LUCKY TRADE OS) — GITHUB AUTO-REDEPLOY SCRIPT
# Chạy script này trên VPS để tự động kéo code mới từ GitHub và cập nhật hệ thống
# ==============================================================================

param(
    [string]$RepoDir = "C:\OPC-AI-TRADER"
)

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  OPC AI TRADER — GITHUB AUTO-UPDATE & REDEPLOYMENT" -ForegroundColor Cyan
Write-Host "  Repo: https://github.com/victorChuyen/Trade-AI-Agentic" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if (Test-Path $RepoDir) {
    Set-Location $RepoDir
}

# 1. Kéo mã nguồn mới nhất từ GitHub
Write-Host "`n>>> [1/5] Kéo mã nguồn mới nhất từ GitHub..." -ForegroundColor Yellow
git config --global --add safe.directory (Get-Location).Path 2>$null
git pull origin main

# 2. Cập nhật thư viện Python nếu có thay đổi
Write-Host "`n>>> [2/5] Kiểm tra và cập nhật dependencies Python..." -ForegroundColor Yellow
if (Test-Path ".\.venv\Scripts\python.exe") {
    & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
    & ".\.venv\Scripts\python.exe" -m pip install -r service\requirements.txt
} else {
    Write-Host ">>> Creating virtual environment .venv..." -ForegroundColor Yellow
    py -3.11 -m venv .venv
    & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
    & ".\.venv\Scripts\python.exe" -m pip install -r service\requirements.txt
}

# 3. Biên dịch Frontend Production (Vite + TypeScript)
Write-Host "`n>>> [3/5] Biên dịch Frontend Production (Vite + TypeScript)..." -ForegroundColor Yellow
if (Test-Path "service\frontend") {
    Push-Location "service\frontend"
    if (-not (Test-Path "node_modules")) {
        npm install --legacy-peer-deps
    }
    npm run build
    Pop-Location
}

# 4. Đảm bảo MetaTrader 5 Terminal đang chạy
Write-Host "`n>>> [4/5] Kiểm tra tiến trình MetaTrader 5..." -ForegroundColor Yellow
$mt5Process = Get-Process terminal64 -ErrorAction SilentlyContinue
if (-not $mt5Process) {
    if (Test-Path "C:\Program Files\MetaTrader 5\terminal64.exe") {
        Write-Host ">>> Khởi chạy MetaTrader 5 Terminal..." -ForegroundColor Cyan
        Start-Process "C:\Program Files\MetaTrader 5\terminal64.exe"
        Start-Sleep -Seconds 3
    }
}

# 5. Khởi động lại dịch vụ Backend Engine
Write-Host "`n>>> [5/5] Khởi động lại Backend Engine trên cổng 8000..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -notlike "*code*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "service\server\main.py" -WindowStyle Minimized

Start-Sleep -Seconds 3

# Kiểm tra sức khỏe dịch vụ
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/mt5/status" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host "  ✅ CẬP NHẬT HOÀN TẤT! HỆ THỐNG ĐANG HOẠT ĐỘNG 24/7" -ForegroundColor Green
    Write-Host "  Web API & UI: http://localhost:8000" -ForegroundColor Green
    Write-Host "  MT5 Connected: $($res.connected) (Account: $($res.login))" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
} catch {
    Write-Host "`n>>> Backend đang khởi động hoặc chưa phản hồi: $_" -ForegroundColor Yellow
}
