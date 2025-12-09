Write-Host "Starting Resort Genius System..." -ForegroundColor Green

# Start Backend
Write-Host "Starting Backend (Port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd backend && python -m uvicorn app.main:app --reload --port 8000" -WindowStyle Normal

# Start Frontend
Write-Host "Starting Frontend (Port 3000)..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd frontend && npm run dev" -WindowStyle Normal

Write-Host "System is starting up!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000"
