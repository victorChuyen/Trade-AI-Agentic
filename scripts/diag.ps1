Write-Host "=== DIAGNOSTIC START ==="
Write-Host ">>> Checking Python Processes:"
Get-Process python -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, Path

Write-Host ">>> Checking Netstat 8000:"
netstat -ano | Select-String "8000"

Write-Host ">>> Checking Windows Firewall Rules:"
Get-NetFirewallRule -DisplayName "OPC-AI-Trader-Ports" | Format-Table Name, DisplayName, Enabled, Direction, Action

Write-Host ">>> Disabling Windows Firewall for testing:"
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

Write-Host ">>> Checking Server Log:"
if (Test-Path "C:\OPC-AI-TRADER\service\server\logs\server.log") {
    Get-Content "C:\OPC-AI-TRADER\service\server\logs\server.log" -Tail 30
} else {
    Write-Host "server.log does not exist!"
}

Write-Host ">>> Starting Server Directly with absolute paths:"
Set-Location "C:\OPC-AI-TRADER"
$py = "C:\OPC-AI-TRADER\.venv\Scripts\python.exe"
$main = "C:\OPC-AI-TRADER\service\server\main.py"
Start-Process -FilePath $py -ArgumentList $main -WorkingDirectory "C:\OPC-AI-TRADER" -WindowStyle Minimized

Start-Sleep -Seconds 3
Write-Host ">>> Netstat after direct start:"
netstat -ano | Select-String "8000"

Write-Host "=== DIAGNOSTIC END ==="
