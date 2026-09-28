# ==============================================================================
# 🏆 OPC AI TRADER (LUCKY TRADE OS) — GITHUB AUTO-REDEPLOY SCRIPT
# Chạy script này trên VPS để tự động kéo code mới từ GitHub và cập nhật hệ thống
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  OPC AI TRADER — GITHUB AUTO-UPDATE & REDEPLOYMENT" -ForegroundColor Cyan
Write-Host "  Repo: https://github.com/victorChuyen/Trade-AI-Agentic" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Kéo mã nguồn mới nhất từ GitHub
Write-Host "`n>>> [1/4] Kéo mã nguồn mới nhất từ GitHub..." -ForegroundColor Yellow
git pull origin main

# 2. Cập nhật thư viện Python nếu có thay đổi
Write-Host "`n>>> [2/4] Kiểm tra và cập nhật dependencies Python..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" -m pip install --upgrade -r service\requirements.txt

# 3. Build gói Frontend Production mới nhất
Write-Host "`n>>> [3/4] Biên dịch Frontend Production (Vite + TypeScript)..." -ForegroundColor Yellow
cd service\frontend
npm run build
cd ..\..

# 4. Khởi động lại dịch vụ Backend Engine
Write-Host "`n>>> [4/4] Khởi động lại Backend Engine trên cổng 8000..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "service\server\main.py" -WindowStyle Minimized

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  ✅ CẬP NHẬT HOÀN TẤT! HỆ THỐNG ĐANG HOẠT ĐỘNG 24/7" -ForegroundColor Green
Write-Host "  Web API: http://localhost:8000" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
