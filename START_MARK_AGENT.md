# 🚀 Start MARK Agent - Quick Commands

## Prerequisites Check

Run the setup script first:
```bash
python setup_mark_agent.py
```

## Fix Missing Dependencies

If beautifulsoup4 is missing:
```bash
pip install beautifulsoup4
```

Or install all dependencies:
```bash
pip install -r backend/requirements.txt
```

## Start Redis (Required for Caching)

### Windows
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Extract and run: `redis-server.exe`

Or use WSL:
```bash
wsl
sudo service redis-server start
```

### Mac
```bash
brew install redis
redis-server
```

### Linux
```bash
sudo apt-get install redis-server
redis-server
```

### Verify Redis is Running
```bash
redis-cli ping
# Should return: PONG
```

## Start Backend

```bash
cd backend
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000

## Start Frontend

In a new terminal:
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## Access MARK Chat Interface

Open your browser:
```
http://localhost:3000/mark-chat
```

## Test the Main Feature

1. You should see a large green button at the top: **"💰 Maximize My Savings"**
2. Click it to get a comprehensive savings analysis
3. Or type: "Show me savings from my transactions"

## Verify Everything is Working

### Check Backend
```bash
curl http://localhost:8000/api/agents/status
```

Should return agent status JSON.

### Check Frontend
Open: http://localhost:3000/mark-chat

You should see:
- ✅ Header with "MARK Assistant"
- ✅ Agent status indicators (MARK 🟢 BH1 🟢 BH2 🟢)
- ✅ **Large green "Maximize My Savings" button** (takes 1/3 space)
- ✅ 3 ideal prompt buttons
- ✅ Chat messages area
- ✅ Input field with send button

### Test the Button
1. Click "💰 Maximize My Savings"
2. Button should show loading state
3. After 2-3 seconds, you should see a comprehensive analysis:
   - Credit card recommendations
   - Coupon savings estimate
   - Investment portfolio breakdown
   - 10-year wealth projection

## Troubleshooting

### Redis Not Running
```bash
# Check if Redis is running
redis-cli ping

# If not, start it
redis-server

# On Windows with WSL
wsl
sudo service redis-server start
```

### Backend Not Starting
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process if needed
taskkill /PID <PID> /F

# Restart backend
cd backend
uvicorn main:app --reload
```

### Frontend Not Starting
```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Kill the process if needed
taskkill /PID <PID> /F

# Restart frontend
npm run dev
```

### Button Not Showing
1. Check browser console for errors (F12)
2. Verify you're on: http://localhost:3000/mark-chat
3. Try hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### No Transactions to Analyze
If you see "I need some transaction data":
1. Connect a bank account via Plaid
2. Or generate test transactions:
   ```bash
   cd backend
   python generate_test_transactions.py
   ```

## Quick Test Commands

### Test Backend API
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"Show me savings"}'

# Test agent status
curl http://localhost:8000/api/agents/status

# Test ideal prompts
curl http://localhost:8000/api/agents/ideal-prompts

# Test RAG stats
curl http://localhost:8000/api/rag/stats
```

### Test Redis
```bash
redis-cli
> ping
PONG
> set test "hello"
OK
> get test
"hello"
> exit
```

## All-in-One Start Script (Windows)

Create a file `start.bat`:
```batch
@echo off
echo Starting MARK Agent...

echo.
echo [1/3] Starting Redis...
start "Redis" redis-server

timeout /t 2

echo.
echo [2/3] Starting Backend...
start "Backend" cmd /k "cd backend && uvicorn main:app --reload"

timeout /t 3

echo.
echo [3/3] Starting Frontend...
start "Frontend" cmd /k "npm run dev"

echo.
echo ✅ All services started!
echo.
echo Open: http://localhost:3000/mark-chat
echo.
pause
```

Run: `start.bat`

## All-in-One Start Script (Mac/Linux)

Create a file `start.sh`:
```bash
#!/bin/bash

echo "Starting MARK Agent..."

echo ""
echo "[1/3] Starting Redis..."
redis-server &
sleep 2

echo ""
echo "[2/3] Starting Backend..."
cd backend
uvicorn main:app --reload &
cd ..
sleep 3

echo ""
echo "[3/3] Starting Frontend..."
npm run dev &

echo ""
echo "✅ All services started!"
echo ""
echo "Open: http://localhost:3000/mark-chat"
echo ""
```

Make executable and run:
```bash
chmod +x start.sh
./start.sh
```

## Stop All Services

### Windows
```batch
taskkill /F /IM redis-server.exe
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

### Mac/Linux
```bash
pkill redis-server
pkill -f uvicorn
pkill -f "npm run dev"
```

## Success Indicators

When everything is working, you should see:

### Terminal 1 (Redis)
```
[PID] Ready to accept connections
```

### Terminal 2 (Backend)
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ Redis cache connected
✅ RAG Service initialized
👔 MARK Agent initialized with enhanced capabilities!
```

### Terminal 3 (Frontend)
```
✓ Ready in 2.3s
○ Local:   http://localhost:3000
```

### Browser
- Large green "Maximize My Savings" button visible
- Agent status showing: MARK 🟢 BH1 🟢 BH2 🟢
- Chat interface responsive and working

## 🎉 You're Ready!

Click the big green button and watch MARK analyze your finances!

---

**Quick Reference:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000/mark-chat
- API Docs: http://localhost:8000/docs
- Redis: localhost:6379
