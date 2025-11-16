# 🚀 Chat Interface Quick Start Guide

## ✅ What's Working

1. **Chat UI** - Dashboard shrinks to 2/3, chat panel at 1/3
2. **Agent Cards** - BountyHunter1 & BountyHunter2 shown at top of chat
3. **LLM Integration** - OpenRouter (Claude 3.5 Sonnet) + Gemini 2.0 Flash fallback
4. **MCP Agents** - MARK, BountyHunter1, BountyHunter2 all initialized
5. **Finance News** - 33 articles already scraped from Yahoo Finance

## 🎯 How to Start

### 1. Start the Backend

```bash
cd backend
python main.py
```

You should see:
```
🚀 Starting BuckBounty API with MCP Agents...
🤖 BountyHunter1 initialized with capabilities: ...
🤖 BountyHunter2 initialized with capabilities: ...
👔 MARK Agent initialized - Ready to assist!
✅ All agents initialized and ready!
```

### 2. Start the Frontend

In a new terminal:

```bash
npm run dev
```

### 3. Test the Chat

1. Open `http://localhost:3000`
2. Connect to Plaid (if needed)
3. Click the **🤖 MARK icon** in the bottom-right corner
4. Chat panel slides in from the right
5. See the 2 agent cards at the top:
   - 🎯 BountyHunter1 - Coupon & Deal Hunter
   - 📊 BountyHunter2 - Finance News Analyst

### 4. Try These Prompts

**General Help**:
```
Hello! What can you do?
```

**Finance News** (uses BountyHunter2):
```
What's happening in the market?
Tell me about recent finance news
What are the latest economic trends?
```

**Coupon Search** (uses BountyHunter1):
```
Find me some coupons
Do you have any deals for UberEats?
Show me discount codes
```

**Budget Advice** (uses MARK):
```
Should I spend $500 on a new laptop?
Help me create a budget
How much should I save each month?
```

## 🧪 Testing Results

### LLM Test
```bash
cd backend
python test_llm.py
```

✅ **Results**:
- OpenRouter API: ✅ Working
- Gemini API: ✅ Working
- Claude 3.5 Sonnet: ✅ Responding
- Sample response: "Cook meals at home instead of eating out to save hundreds of dollars each month."

### Chat Test
```bash
cd backend
python test_chat.py
```

✅ **Results**:
- MARK Agent: ✅ Responding
- BountyHunter1: ✅ Ready (0 coupons loaded)
- BountyHunter2: ✅ Ready (33 news articles loaded)
- MCP Server: ✅ Routing requests

## 📊 Current Data

**Finance News** (BountyHunter2):
- **33 articles** scraped from Yahoo Finance
- Located: `backend/data/finance_news/finance_news.json`
- Categories: general, economy, markets
- Sample headlines:
  - "Ducati expands into off-road motorcycles..."
  - "Ex-Fed Governor Kugler quit after trading violations..."
  - "Trump bought at least $82M in bonds..."
  - "IRS boosts contribution limits for 401(k) savers..."

**Coupons** (BountyHunter1):
- **0 coupons** currently (Gmail API not configured)
- Can be populated by:
  1. Setting up Gmail API (optional)
  2. Running manual scrape of Honey/Rakuten

## 🎨 UI Features

### Chat Interface
- **Header**: MARK Assistant with close button
- **Agent Cards**: 2 cards showing BountyHunter1 & BountyHunter2
  - Green pulse indicator when active
  - Agent name, emoji, and description
- **Messages**: Clean chat bubbles with agent attribution
- **Input**: Text input + voice button + send button
- **Status**: Agent online/offline indicators at bottom

### Dashboard Layout
- **Closed**: Dashboard full width
- **Open**: Dashboard 2/3 width, chat 1/3 width
- **Smooth transitions** between states
- **MARK icon** pulses in bottom-right

## 🔑 API Configuration

Already configured in `.env`:
```bash
OPENROUTER_API_KEY=your_key  # ✅ Set
GEMINI_API_KEY=your_key      # ✅ Set
```

**Models Used**:
- Primary: `anthropic/claude-3.5-sonnet` (via OpenRouter)
- Fallback: `gemini-2.0-flash-exp` (via Gemini API)

## 🐛 Troubleshooting

### Chat not connecting
1. Make sure backend is running on port 8000
2. Check browser console for errors
3. Verify `http://localhost:8000/api/agents/status` returns agent info

### No responses from agents
1. Check `.env` has API keys
2. Test with: `cd backend && python test_llm.py`
3. Check backend logs for errors

### Agent cards not showing
1. Make sure you clicked the MARK icon
2. Check browser console
3. Verify ChatInterface component loaded

### Finance news not showing
1. BountyHunter2 has 33 articles ready
2. Try: "What's happening in the market?"
3. Check: `backend/data/finance_news/finance_news.json`

## 📈 Next Steps

### To Populate Coupons (BountyHunter1)

**Option 1: Manual Scrape**
```bash
curl -X POST http://localhost:8000/api/agents/bounty-hunter-1/scrape
```

**Option 2: Set up Gmail API**
1. Follow instructions in `AGENTS_README.md`
2. Configure OAuth credentials
3. BountyHunter1 will read UberEats/DoorDash emails

### To Refresh Finance News (BountyHunter2)

Automatically runs every 24 hours, or manually:
```bash
curl -X POST http://localhost:8000/api/agents/bounty-hunter-2/scrape
```

## 🎯 Example Conversation

```
You: Hi MARK!
MARK: Hey there! I'm MARK, your personal finance assistant.
      How can I help you save money today?

You: What's happening in the market?
BountyHunter2: Based on the latest Yahoo Finance news, here are
               the key market trends:

               1. IRS has boosted 401(k) contribution limits for 2026
               2. Recent Fed policy changes affecting interest rates
               3. Market volatility in tech sector

               Would you like me to dive deeper into any of these?

You: Find me some food delivery coupons
BountyHunter1: I'm currently working on gathering the latest coupons!
               My database is being populated. In the meantime, I can
               help you with budgeting tips for food delivery expenses!

You: Should I spend $200 on dining out this month?
MARK: Based on your spending patterns, here's my analysis:
      - Your average monthly food spending: $450
      - $200 for dining out is reasonable if you balance it with groceries
      - Consider using coupons to reduce the cost further

      Would you like me to help you find deals?
```

## ✨ Features

- ✅ Real-time chat with LLM responses
- ✅ Multi-agent orchestration
- ✅ OpenRouter + Gemini fallback
- ✅ Agent status indicators
- ✅ Conversation history
- ✅ Voice input button (UI ready)
- ✅ Smooth animations
- ✅ Responsive design

## 📚 Documentation

- **Complete Guide**: [AGENTS_README.md](AGENTS_README.md)
- **Blueprint**: [BLUEPRINT.md](BLUEPRINT.md)
- **Bill Split**: [BILL_SPLIT_FEATURE.md](BILL_SPLIT_FEATURE.md)

---

**Ready to chat! Click the 🤖 icon and start saving money!** 💰
