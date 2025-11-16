@echo off
echo ============================================================
echo BuckBounty Setup Verification
echo ============================================================
echo.

echo Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found
    goto :error
)
echo ✅ Python installed
echo.

echo Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js not found
    goto :error
)
echo ✅ Node.js installed
echo.

echo Checking npm...
npm --version
if %errorlevel% neq 0 (
    echo ❌ npm not found
    goto :error
)
echo ✅ npm installed
echo.

echo Checking Redis...
if exist "D:\Redis\redis-server.exe" (
    echo ✅ Redis installed at D:\Redis\
) else (
    echo ❌ Redis not found at D:\Redis\
    goto :error
)
echo.

echo Checking backend files...
if exist "backend\main.py" (
    echo ✅ Backend files present
) else (
    echo ❌ Backend files missing
    goto :error
)
echo.

echo Checking frontend files...
if exist "package.json" (
    echo ✅ Frontend files present
) else (
    echo ❌ Frontend files missing
    goto :error
)
echo.

echo Checking components...
if exist "components\MarkChatInterface.tsx" (
    echo ✅ MARK Chat component present
) else (
    echo ❌ MARK Chat component missing
    goto :error
)
echo.

echo Checking startup scripts...
if exist "START_ALL.bat" (
    echo ✅ Startup scripts present
) else (
    echo ❌ Startup scripts missing
    goto :error
)
echo.

echo ============================================================
echo ✅ All checks passed!
echo ============================================================
echo.
echo You're ready to start BuckBounty!
echo.
echo Next steps:
echo 1. Double-click START_ALL.bat
echo 2. Wait for all services to start
echo 3. Open http://localhost:3000/mark-chat
echo 4. Click the green "Maximize My Savings" button
echo.
goto :end

:error
echo.
echo ============================================================
echo ❌ Setup verification failed
echo ============================================================
echo.
echo Please check the errors above and fix them.
echo Refer to HOW_TO_START.md for help.
echo.

:end
pause
