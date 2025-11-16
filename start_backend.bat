@echo off
echo ============================================================
echo Starting BuckBounty Backend
echo ============================================================
echo.

cd backend
uvicorn main:app --reload

pause
