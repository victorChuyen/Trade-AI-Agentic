# ==============================================================================
# 🏆 OPC AI TRADER (LUCKY TRADE OS) — WINDOWS VPS 24/7 AUTO-PROVISIONING SCRIPT
# Run this script in PowerShell as Administrator on opc-trade-win-01 (34.87.156.228)
# ==============================================================================

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$logDir = "C:\OPC-AI-TRADER\logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}
$logPath = "C:\OPC-AI-TRADER\logs\bootstrap.log"

function Log-Message([string]$msg, [string]$color = "Cyan") {
    $time = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$time] $msg"
    Write-Host $line -ForegroundColor $color
    Add-Content -Path $logPath -Value $line -Encoding utf8
}

Log-Message "==========================================================" "Green"
Log-Message "  STARTING OPC AI TRADER FULL VPS AUTOMATED PROVISIONING  " "Green"
Log-Message "==========================================================" "Green"

# 1. Execution Policy & TLS
Log-Message ">>> [1/7] Configuring Execution Policy & TLS 1.2..."
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

# 2. Install Chocolatey if not present
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Log-Message ">>> Installing Chocolatey..." "Yellow"
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Refresh Environment
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 3. Install Git, Python 3.11, Node.js
Log-Message ">>> [2/7] Installing Git, Python 3.11, Node.js LTS..."
choco install -y git python311 nodejs-lts

# Refresh Environment
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 4. Install MetaTrader 5 Terminal
Log-Message ">>> [3/7] Installing MetaTrader 5 Terminal..."
$mt5Path = "$env:TEMP\mt5setup.exe"
if (-not (Test-Path "C:\Program Files\MetaTrader 5\terminal64.exe")) {
    Invoke-WebRequest -Uri "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe" -OutFile $mt5Path
    Start-Process -FilePath $mt5Path -ArgumentList "/auto" -Wait
    Start-Sleep -Seconds 5
}
Log-Message ">>> MetaTrader 5 Terminal ready at C:\Program Files\MetaTrader 5\terminal64.exe" "Green"

# 5. Setup Project Repository
Log-Message ">>> [4/7] Setting up repository at C:\OPC-AI-TRADER..."
$repoDir = "C:\OPC-AI-TRADER"
if (-not (Test-Path "$repoDir\.git")) {
    git clone https://github.com/victorChuyen/Trade-AI-Agentic.git $repoDir
} else {
    Set-Location $repoDir
    git config --global --add safe.directory $repoDir 2>$null
    git pull origin main
}

Set-Location $repoDir

# 6. Generate Production Configuration (.env & Firebase Admin SDK)
Log-Message ">>> [5/7] Writing Production .env and Firebase credentials..."

$envContent = @"
# ==================== OPC AI TRADER / LUCKY TRADE OS ====================
ENVIRONMENT=production

# ==================== Database ====================
DATABASE_URL=
DB_PATH=service/server/data/opc_trader.db

# ==================== AI Brain: 9Router AI Gateway ====================
OPENROUTER_BASE_URL=https://api.breaths.live/v1
OPENROUTER_API_KEY=sk-7c1f91635f52dc7e-fcsworkforce-2026
OPENROUTER_MODEL=cx/gpt-6-astra
AI_BASE_URL=https://api.breaths.live/v1
AI_API_KEY=sk-7c1f91635f52dc7e-fcsworkforce-2026
AI_MODEL=cx/gpt-6-astra

# ==================== MetaTrader 5 / FTMO Account ====================
LUCKY_MT5_LOGIN=5056580335
LUCKY_MT5_PASSWORD=_iDgN8Bs
LUCKY_MT5_INVESTOR_PASSWORD=_p0pRsTo
LUCKY_MT5_SERVER=MetaQuotes-Demo
LUCKY_MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
LUCKY_MT5_MAGIC=202688

# ==================== FTMO Drawdown Guard (Gate 2) ====================
FTMO_MAX_DAILY_LOSS_PCT=5.0
FTMO_MAX_TOTAL_LOSS_PCT=10.0
FTMO_SAFETY_TRIGGER_DAILY_PCT=4.5
FTMO_SAFETY_TRIGGER_TOTAL_PCT=9.0

# ==================== Market Data ====================
ALPHA_VANTAGE_API_KEY=demo
ADANOS_API_KEY=
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz/info

# ==================== Network / CORS ====================
CLAWTRADER_CORS_ORIGINS=http://localhost:3000,http://localhost:3005,http://localhost:8000,https://trade.breaths.live

# ==================== Firebase Authentication & RBAC ====================
FIREBASE_PROJECT_ID=opc-ai-trader
FIREBASE_SERVICE_ACCOUNT_KEY=opc-ai-trader-firebase-adminsdk-fbsvc-17705c7301.json
FIREBASE_SUPER_ADMIN_EMAILS=coach.chuyen@gmail.com,tranngocchuyen1980@gmail.com
FIREBASE_SUPER_ADMIN_UIDS=i6C5uQ9lBnfCaekEPu68DPvK2QS2,bQXfjcvt3hYfhR1OYyQTC1UfbBF2

# ==================== Firebase Client (Vite) ====================
VITE_FIREBASE_API_KEY=AIzaSyCbrDs10N1Qqb7kII9keLN7uEW3UzCgpxo
VITE_FIREBASE_AUTH_DOMAIN=opc-ai-trader.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=opc-ai-trader
VITE_FIREBASE_STORAGE_BUCKET=opc-ai-trader.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=371100655035
VITE_FIREBASE_APP_ID=1:371100655035:web:8fa8662a7703036872f89e
VITE_FIREBASE_MEASUREMENT_ID=G-0CLRVZ5LVV
"@

Set-Content -Path "C:\OPC-AI-TRADER\.env" -Value $envContent -Encoding utf8

$serviceAccountKeyDest = "C:\OPC-AI-TRADER\opc-ai-trader-firebase-adminsdk-fbsvc-17705c7301.json"
if (-not (Test-Path $serviceAccountKeyDest)) {
    if ($env:FIREBASE_SERVICE_ACCOUNT_KEY_CONTENT) {
        Set-Content -Path $serviceAccountKeyDest -Value $env:FIREBASE_SERVICE_ACCOUNT_KEY_CONTENT -Encoding utf8
    } elseif (Test-Path "$env:TEMP\opc-ai-trader-firebase-adminsdk.json") {
        Copy-Item "$env:TEMP\opc-ai-trader-firebase-adminsdk.json" $serviceAccountKeyDest -Force
    } else {
        Log-Message ">>> NOTE: Place Firebase Service Account JSON at $serviceAccountKeyDest" "Yellow"
    }
}


# 7. Setup Python Environment and Dependencies
Log-Message ">>> [6/7] Setting up Python virtual environment and dependencies..."
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    py -3.11 -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r service\requirements.txt

# Build Frontend
if (Test-Path "service\frontend") {
    Log-Message ">>> Building Frontend Production Bundle..."
    Push-Location "service\frontend"
    npm install --legacy-peer-deps
    npm run build
    Pop-Location
}

# 8. Install Auto-Deploy Service and Launch
Log-Message ">>> [7/7] Registering Auto-Deploy Service & Launching Trading Engine..."
& powershell -ExecutionPolicy Bypass -File ".\scripts\install_auto_deploy_service.ps1"

Log-Message "==========================================================" "Green"
Log-Message "  🎉 PROVISIONING SUCCESSFUL! SYSTEM IS LIVE ON PORT 8000 " "Green"
Log-Message "  Dashboard & API: http://localhost:8000" "Green"
Log-Message "==========================================================" "Green"
