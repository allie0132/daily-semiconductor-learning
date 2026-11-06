# Starts (or restarts) the ATE dashboard under its own executable name
# "pydash.exe" so it never collides with python.exe processes (e.g. life_bot.py).
#
# Usage:  powershell -ExecutionPolicy Bypass -File run_dashboard.ps1

$ErrorActionPreference = "SilentlyContinue"

$pyDir = "C:\Users\oarcl\AppData\Local\Programs\Python\Python39"
$pyExe = Join-Path $pyDir "python.exe"
$dash  = Join-Path $pyDir "pydash.exe"
$appDir = "C:\Users\oarcl\Claude Code\daily-semiconductor-learning\test-dashboard"

# Ensure the renamed interpreter exists (re-copy after a Python upgrade).
if (-not (Test-Path $dash)) {
    Copy-Item $pyExe $dash -Force
    Write-Host "Created $dash"
}

# Stop any existing dashboard instance (only pydash.exe — leaves python.exe alone).
Get-Process pydash -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 600

# Launch the dashboard.
Start-Process -FilePath $dash -ArgumentList "app.py" -WorkingDirectory $appDir -WindowStyle Hidden
Start-Sleep -Seconds 4

# Report status.
$proc = Get-Process pydash -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host ("Dashboard started under pydash.exe (PID {0})" -f ($proc.Id -join ", "))
    Write-Host "Open: http://localhost:5001"
} else {
    Write-Host "Dashboard failed to start. Run it directly to see the error:"
    Write-Host ("  & '{0}' app.py   (from {1})" -f $dash, $appDir)
}
