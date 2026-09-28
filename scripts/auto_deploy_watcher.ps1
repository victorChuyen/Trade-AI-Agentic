# ==============================================================================
# 🏆 OPC AI TRADER (LUCKY TRADE OS) — GITHUB CONTINUOUS AUTO-DEPLOY WATCHER
# Runs 24/7 on Windows VPS to auto-pull & auto-deploy whenever GitHub main updates
# ==============================================================================

param(
    [string]$RepoDir = "C:\OPC-AI-TRADER",
    [int]$IntervalSeconds = 60
)

$ErrorActionPreference = "Continue"
$logDir = Join-Path $RepoDir "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}
$logFile = Join-Path $logDir "auto_deploy.log"

function Write-DeployLog([string]$Message, [string]$Level = "INFO") {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $logLine = "[$timestamp] [$Level] $Message"
    Write-Host $logLine
    Add-Content -Path $logFile -Value $logLine -Encoding utf8
}

Write-DeployLog ">>> Starting OPC AI Trader Auto-Deploy Watcher on $RepoDir (Check interval: ${IntervalSeconds}s)"

if (-not (Test-Path $RepoDir)) {
    Write-DeployLog "Repository directory $RepoDir does not exist! Exiting." "ERROR"
    exit 1
}

Set-Location $RepoDir

# Ensure Git safe directory
git config --global --add safe.directory $RepoDir 2>$null

while ($true) {
    try {
        # Fetch remote origin
        $fetchOutput = git fetch origin main 2>&1
        $localCommit = (git rev-parse HEAD).Trim()
        $remoteCommit = (git rev-parse origin/main).Trim()

        if ($localCommit -ne $remoteCommit) {
            Write-DeployLog ">>> NEW COMMIT DETECTED ON GITHUB! Local: $localCommit -> Remote: $remoteCommit" "UPDATE"
            
            # Execute deployment script
            $deployScript = Join-Path $RepoDir "scripts\update_and_deploy.ps1"
            if (Test-Path $deployScript) {
                Write-DeployLog ">>> Executing update_and_deploy.ps1..." "INFO"
                & powershell -ExecutionPolicy Bypass -File $deployScript
                Write-DeployLog ">>> Auto-deployment completed successfully for commit: $remoteCommit" "SUCCESS"
            } else {
                # Fallback manual pull & restart
                Write-DeployLog ">>> update_and_deploy.ps1 not found, running inline update..." "WARN"
                git pull origin main
                & ".\.venv\Scripts\python.exe" -m pip install -r service\requirements.txt
                Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
                Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "service\server\main.py" -WindowStyle Minimized
                Write-DeployLog ">>> Inline update complete!" "SUCCESS"
            }
        }
    } catch {
        Write-DeployLog "Error during check/deploy: $_" "ERROR"
    }

    Start-Sleep -Seconds $IntervalSeconds
}
