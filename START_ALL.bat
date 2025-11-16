@echo off
echo ============================================================
echo Starting BuckBounty - Complete System
echo ============================================================
echo.

echo [1/3] Starting Redis Server...
start "Redis Server" cmd /k "D:\Redis\redis-server.exe redis.windows.conf"
timeout /t 2 /nobreak >nul

echo [2/3] Starting Backend API...
start "Backend API" cmd /k "cd backend && uvicorn main:app --reload"
timeout /t 5 /nobreak >nul

echo [3/3] Starting Frontend...
start "Frontend" cmd /k "npm run dev"

echo.
echo ============================================================
echo All services started!
echo ============================================================
echo.
echo Redis:    Running on port 6379
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Open your browser: http://localhost:3000/mark-chat
echo.
echo Press any key to exit (services will keep running)...
pause >nul
