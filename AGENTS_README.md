# 🤖 BuckBounty MCP Multi-Agent System

## Overview

BuckBounty now features a complete MCP (Model Context Protocol) multi-agent system with 3 specialized AI agents working together to provide comprehensive financial assistance.

## Architecture

```
┌──────────────────────────────────────────┐
│         User Interface (Chat UI)          │
└───────────────┬──────────────────────────┘
                │
┌───────────────▼──────────────────────────┐
│         MCP Server (Orchestration)        │
└───────────────┬──────────────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼────┐  ┌──────▼────────┐  ┌────────▼──────┐
│    MARK    │  │ BountyHunter1 │  │ BountyHunter2 │
│   (Main)   │  │   (Coupons)   │  │  (FinNews)    │
└────────────┘  └───────────────┘  └───────────────┘
```

## Agents

### 1. MARK (Main Agent)

**Role**: Primary orchestrator and financial advisor

**Capabilities**:
- Financial advice and budget analysis
- Spending insights and patterns
- Agent orchestration and routing
- Conversation management
- Multi-modal processing

**LLM**: OpenRouter (Claude 3.5 Sonnet) with Gemini 2.0 Flash fallback

**Location**: `backend/agents/mark_agent.py`

### 2. BountyHunter1 (Coupon Hunter)

**Role**: Finds and manages coupon codes and deals

**Capabilities**:
- Gmail integration (UberEats, DoorDash coupons)
- Honey.com scraping
- Rakuten.com scraping
- JSON storage (`data/coupons/all_coupons.json`)
- Vector DB integration for semantic search

**Data Sources**:
- Gmail API (requires OAuth setup)
- https://www.joinhoney.com/explore
- https://www.rakuten.com/

**Execution**: On-demand (triggered by user or manual API call)

**Location**: `backend/agents/bounty_hunter_1.py`

### 3. BountyHunter2 (Finance News)

**Role**: Tracks finance news and market trends

**Capabilities**:
- Yahoo Finance scraping (general + sector news)
- Transaction context analysis
- Personalized news filtering
- JSON storage (`data/finance_news/finance_news.json`)
- 24-hour automatic scheduling

**Data Sources**:
- https://finance.yahoo.com/
- Category-specific Yahoo Finance pages

**Execution**: Automatically every 24 hours + on-demand

**Location**: `backend/agents/bounty_hunter_2.py`

## MCP Server

**Location**: `backend/agents/mcp_server.py`

**Features**:
- Agent registration and lifecycle management
- Request routing to appropriate agents
- Session management per user
- Inter-agent communication (broadcast)
- Status monitoring

## Scheduler

**Location**: `backend/agents/scheduler.py`

**Features**:
- Periodic task execution
- Configurable intervals (hours)
- Run-immediately option
- Status tracking

**Currently scheduled**:
- BountyHunter2 finance news scraping (every 24 hours)

## API Endpoints

### Chat Endpoints

```
POST /api/agents/chat
```
Chat with MARK and the agent team.

**Request**:
```json
{
  "user_id": "user_123",
  "message": "Find me some food delivery coupons",
  "conversation_history": [],
  "target_agent": null
}
```

**Response**:
```json
{
  "success": true,
  "agent": "mark",
  "response": "I found several coupons for you...",
  "data": {},
  "timestamp": "2025-11-15T10:30:00"
}
```

### Status Endpoints

```
GET /api/agents/status
```
Get status of all agents and MCP server.

```
GET /api/agents/bounty-hunter-1/coupons?query=ubereats
```
Get coupons (optionally filtered by query).

```
GET /api/agents/bounty-hunter-2/news?query=market
```
Get finance news (optionally filtered by query).

### Manual Trigger Endpoints

```
POST /api/agents/bounty-hunter-1/scrape
```
Manually trigger BountyHunter1 coupon scraping.

```
POST /api/agents/bounty-hunter-2/scrape
```
Manually trigger BountyHunter2 finance news scraping.

## Chat Interface

### Features

- **Responsive Layout**: Dashboard shrinks to 2/3 width when chat opens
- **Chat Panel**: 1/3 width sidebar with full-height chat
- **Voice Input**: Voice button for speech-to-text (placeholder)
- **Agent Indicators**: Shows which agent is responding
- **Status Badges**: Real-time agent online/offline status

### Usage

1. Click the MARK agent icon (🤖) in the bottom-right corner
2. Chat panel slides in from the right
3. Type messages or use voice input
4. MARK routes your request to appropriate agents
5. Click X to close the chat panel

## Environment Setup

### Required API Keys

Add these to your `.env` file:

```bash
# Primary LLM (OpenRouter with Claude)
OPENROUTER_API_KEY=your_openrouter_key

# Fallback LLM
GEMINI_API_KEY=your_gemini_key

# Optional: Gmail API (for BountyHunter1)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_secret
```

### Optional: Gmail API Setup

For BountyHunter1 to read emails:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials and save as `backend/credentials/gmail_credentials.json`
6. Run OAuth flow to generate `gmail_token.json`

Without Gmail API, BountyHunter1 will still scrape Honey and Rakuten.

## Installation

### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parsing
- `google-auth*` - Gmail API (optional)

### Frontend Dependencies

No new frontend dependencies needed.

## Running the System

### 1. Start Backend (with agents)

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
✅ Agent registered: mark
✅ Agent registered: bounty_hunter_1
✅ Agent registered: bounty_hunter_2
✅ MCP Server started
📅 Scheduled task 'bh2_finance_news_scrape' to run every 24 hours
⏰ Agent scheduler started
✅ All agents initialized and ready!
```

### 2. Start Frontend

```bash
npm run dev
```

### 3. Test Agents (Optional)

```bash
cd backend
python test_agents.py
```

This will:
- Run BountyHunter1 coupon scraping
- Run BountyHunter2 finance news scraping
- Generate JSON files
- Push data to vector DB

## Data Storage

### Coupons

**File**: `backend/data/coupons/all_coupons.json`

**Structure**:
```json
[
  {
    "id": "honey_Amazon_1731664200.123",
    "source": "honey",
    "merchant": "Amazon",
    "code": "SAVE20",
    "description": "20% off electronics",
    "found_date": "2025-11-15T10:30:00",
    "url": "https://...",
    "category": "general"
  }
]
```

### Finance News

**File**: `backend/data/finance_news/finance_news.json`

**Structure**:
```json
[
  {
    "id": "yahoo_general_1234567890",
    "source": "yahoo_finance",
    "category": "general",
    "headline": "Market reaches new highs...",
    "summary": "Detailed summary...",
    "url": "https://finance.yahoo.com/...",
    "scraped_date": "2025-11-15T10:30:00"
  }
]
```

### Last Scrape Timestamp

**File**: `backend/data/finance_news/last_scrape.json`

Tracks when BountyHunter2 last ran (for 24-hour scheduling).

## Conversation Examples

### Example 1: Coupon Search

**User**: "Find me UberEats coupons"

**MARK** → Routes to **BountyHunter1**

**BountyHunter1**:
- Searches coupon database for "ubereats"
- Uses Claude/Gemini to format response
- Returns formatted coupon list

### Example 2: Finance News

**User**: "What's happening in the market?"

**MARK** → Routes to **BountyHunter2**

**BountyHunter2**:
- Retrieves recent Yahoo Finance articles
- Matches to user's transaction categories
- Uses Claude/Gemini to summarize news
- Returns personalized insights

### Example 3: Budget Advice

**User**: "Should I spend $500 on this laptop?"

**MARK** → Handles directly

**MARK**:
- Retrieves user's budget and spending
- Analyzes affordability
- Uses Claude/Gemini for advice
- Returns personalized recommendation

## Troubleshooting

### Agents not responding

1. Check that backend is running: `http://localhost:8000/docs`
2. Check agent status: `GET http://localhost:8000/api/agents/status`
3. Verify API keys in `.env`

### No coupons found

- Gmail API may not be configured (expected)
- Honey/Rakuten may have changed HTML structure
- Check logs for scraping errors

### No finance news

- Check internet connection
- Yahoo Finance may be blocking requests
- Try manual scrape: `POST /api/agents/bounty-hunter-2/scrape`

### Import errors

```bash
cd backend
pip install -r requirements.txt
```

## Future Enhancements

### Planned Features

1. **Voice Assistant**: Real speech-to-text for voice button
2. **More Data Sources**: Additional coupon/news sites
3. **Smart Notifications**: Proactive deal alerts
4. **Agent Learning**: Personalization over time
5. **Investment Agent**: Stock/crypto analysis
6. **Bill Split Agent**: Receipt parsing integration

### Additional Scrapers

- RetailMeNot
- Slickdeals
- Google News
- Bloomberg
- CNBC

## Architecture Decisions

### Why MCP?

- **Modularity**: Each agent is independent
- **Scalability**: Easy to add new agents
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Agents can work together or independently

### Why OpenRouter + Gemini?

- **OpenRouter**: Access to Claude (best reasoning)
- **Gemini**: Free tier, fast, good fallback
- **Reliability**: Automatic failover

### Why Background Scheduling?

- **Efficiency**: Don't scrape on every request
- **Rate Limiting**: Respect source websites
- **Freshness**: Regular updates without user action

## Contributing

To add a new agent:

1. Create agent file in `backend/agents/`
2. Extend `BaseAgent` class
3. Implement `process_request()` method
4. Register in `main.py`
5. Add endpoints if needed

## License

Same as BuckBounty project.

---

**Last Updated**: November 2025
**Version**: 1.0.0
**Status**: Production Ready
