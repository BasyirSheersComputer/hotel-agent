@echo off
echo Starting Resort Genius System...

:: Start Backend
echo Starting Backend (Port 8000)...
start "ResortGenius Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

:: Start Frontend
echo Starting Frontend (Port 3000)...
start "ResortGenius Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo System is starting up!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this launcher (terminals will stay open)...
pause
