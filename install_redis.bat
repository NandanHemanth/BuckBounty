@echo off
echo ============================================================
echo Redis Installation for Windows
echo ============================================================
echo.

echo This script will help you install Redis on Windows.
echo.
echo Choose an option:
echo 1. Download Memurai (Recommended - Easy installer)
echo 2. Download Redis for Windows (Manual setup)
echo 3. Use Docker (If you have Docker Desktop)
echo 4. Use WSL (If you have Windows Subsystem for Linux)
echo 5. Skip (I'll install manually)
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Opening Memurai download page...
    echo Please download and install Memurai from the browser.
    start https://www.memurai.com/get-memurai
    echo.
    echo After installation:
    echo 1. Memurai will start automatically
    echo 2. Run: python setup_mark_agent.py
    echo 3. You should see: Redis is running
    pause
    exit
)

if "%choice%"=="2" (
    echo.
    echo Opening Redis for Windows download page...
    echo Please download Redis-x64-3.0.504.zip
    start https://github.com/microsoftarchive/redis/releases
    echo.
    echo After download:
    echo 1. Extract to C:\Redis
    echo 2. Open PowerShell in C:\Redis
    echo 3. Run: redis-server.exe
    pause
    exit
)

if "%choice%"=="3" (
    echo.
    echo Installing Redis via Docker...
    docker pull redis
    docker run -d -p 6379:6379 --name redis redis
    echo.
    echo Testing connection...
    timeout /t 2
    docker exec -it redis redis-cli ping
    echo.
    echo If you see PONG, Redis is running!
    pause
    exit
)

if "%choice%"=="4" (
    echo.
    echo Installing Redis via WSL...
    wsl sudo apt-get update
    wsl sudo apt-get install -y redis-server
    wsl sudo service redis-server start
    echo.
    echo Testing connection...
    wsl redis-cli ping
    echo.
    echo If you see PONG, Redis is running!
    pause
    exit
)

if "%choice%"=="5" (
    echo.
    echo Skipping automatic installation.
    echo Please install Redis manually and run: python setup_mark_agent.py
    pause
    exit
)

echo Invalid choice. Please run the script again.
pause
