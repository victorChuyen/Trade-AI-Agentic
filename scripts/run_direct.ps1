Set-Location "C:\OPC-AI-TRADER"
$py = "C:\OPC-AI-TRADER\.venv\Scripts\python.exe"
$main = "C:\OPC-AI-TRADER\service\server\main.py"
Write-Host ">>> RUNNING PYTHON DIRECTLY AND CAPTURING OUTPUT:"
$output = & $py $main 2>&1
Write-Host ">>> EXIT CODE: $LASTEXITCODE"
Write-Host ">>> OUTPUT: $output"
