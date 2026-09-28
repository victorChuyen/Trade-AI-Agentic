# ==============================================================================
# 🏆 OPC AI TRADER (LUCKY TRADE OS) — INSTALL AUTO-DEPLOY SCHEDULED TASKS
# Chạy script này trên VPS để cài đặt dịch vụ tự động khởi động và auto-deploy
# ==============================================================================

param(
    [string]$RepoDir = "C:\OPC-AI-TRADER"
)

$ErrorActionPreference = "Stop"

Write-Host ">>> [1/3] Cấu hình Windows Firewall cho Cổng 8000, 3000, 3005..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "OPC-AI-Trader-Ports" -Direction Inbound -LocalPort 8000,3000,3005 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null

Write-Host ">>> [2/3] Cài đặt Scheduled Task: OPC-AI-Trader-Engine (Khởi động cùng Windows)..." -ForegroundColor Cyan
$actionEngine = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$RepoDir\scripts\update_and_deploy.ps1`""
$triggerEngine = New-ScheduledTaskTrigger -AtStartup
$principalEngine = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settingsEngine = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Unregister-ScheduledTask -TaskName "OPC-AI-Trader-Engine" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "OPC-AI-Trader-Engine" -Action $actionEngine -Trigger $triggerEngine -Principal $principalEngine -Settings $settingsEngine | Out-Null
Write-Host "  ✅ Đã đăng ký task: OPC-AI-Trader-Engine" -ForegroundColor Green

Write-Host ">>> [3/3] Cài đặt Scheduled Task: OPC-AI-Trader-AutoDeploy (Kiểm tra GitHub mỗi 2 phút)..." -ForegroundColor Cyan
$actionDeploy = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$RepoDir\scripts\auto_deploy_watcher.ps1`""
$triggerDeploy = New-ScheduledTaskTrigger -AtStartup
$settingsDeploy = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 365)

Unregister-ScheduledTask -TaskName "OPC-AI-Trader-AutoDeploy" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "OPC-AI-Trader-AutoDeploy" -Action $actionDeploy -Trigger $triggerDeploy -Principal $principalEngine -Settings $settingsDeploy | Out-Null
Write-Host "  ✅ Đã đăng ký task: OPC-AI-Trader-AutoDeploy" -ForegroundColor Green

# Kích hoạt chạy ngay
Start-ScheduledTask -TaskName "OPC-AI-Trader-Engine" -ErrorAction SilentlyContinue
Start-ScheduledTask -TaskName "OPC-AI-Trader-AutoDeploy" -ErrorAction SilentlyContinue

Write-Host ">>> [SUCCESS] AUTO-DEPLOYMENT SERVICE INSTALLED SUCCESSFULLY!" -ForegroundColor Green
Write-Host ">>> Any new commit on GitHub https://github.com/victorChuyen/Trade-AI-Agentic will auto-deploy within 60s." -ForegroundColor Green

