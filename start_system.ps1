Write-Host "Starting Resort Genius System..." -ForegroundColor Green

# Function to kill process on port
function Kill-Port {
    param($Port)
    $tcp = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($tcp) {
        Write-Host "Port $Port is in use. Killing process logic initiated..." -ForegroundColor Yellow
        $procId = $tcp.OwningProcess
        
        # Check if it's an array of IDs (sometimes happens)
        if ($procId -is [array]) {
            foreach ($id in $procId) {
                Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
            }
        } else {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
        Write-Host "Freed port $Port" -ForegroundColor Green
    }
}

# Cleanup Ports
Kill-Port 8000
Kill-Port 3000

# Cleanup Lock File
$lockFile = "frontend/.next/dev/lock"
if (Test-Path $lockFile) {
    Write-Host "Removing lock file: $lockFile" -ForegroundColor Yellow
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
}

# Start Backend
Write-Host "Starting Backend (Port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd backend && python -m uvicorn app.main:app --reload --port 8000" -WindowStyle Normal

# Start Frontend
Write-Host "Waiting for Backend to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

Write-Host "Starting Frontend (Port 3000)..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd frontend && npm run dev" -WindowStyle Normal

Write-Host "System is starting up!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000"
Write-Host "Press any key to exit this launcher..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
