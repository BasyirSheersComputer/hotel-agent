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

# Robust Process Killing
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
taskkill /F /IM python.exe /T 2>$null
taskkill /F /IM node.exe /T 2>$null
taskkill /F /IM uvicorn.exe /T 2>$null

# Cleanup Ports (Just in case)
Kill-Port 8000
Kill-Port 8001
Kill-Port 3000

# Cleanup Lock File
$lockFile = "frontend/.next/dev/lock"
if (Test-Path $lockFile) {
    Write-Host "Removing lock file: $lockFile" -ForegroundColor Yellow
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
}

# Start Backend
Write-Host "Starting Backend (Port 8001 to avoid conflicts)..." -ForegroundColor Cyan
# Inject Env Vars for SaaS Mode
$backendEnv = @{
    "DEMO_MODE" = "true";
    "LOCAL_DEV" = "true";
    "NEXT_PUBLIC_API_URL" = "http://localhost:8001";
    "PORT" = "8001"
}
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd backend && set DEMO_MODE=true&& set LOCAL_DEV=true&& python -m uvicorn app.main:app --reload --port 8001" -WindowStyle Normal

# Start Frontend
Write-Host "Waiting for Backend to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host "Starting Frontend (Port 3000)..." -ForegroundColor Cyan
# Ensure Frontend knows about Port 8001 (No trailing space!)
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd frontend && set NEXT_PUBLIC_API_URL=http://localhost:8001&& npm run dev" -WindowStyle Normal

Write-Host "System is starting up!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8001/docs"
Write-Host "Frontend: http://localhost:3000"
Write-Host "Press any key to exit this launcher..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
