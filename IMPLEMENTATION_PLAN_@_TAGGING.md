# @ Tagging Feature Implementation Plan

## Overview
When users tag merchants with "@" (e.g., "@Uber", "@Starbucks"), MARK will:
1. Access transaction data for that merchant
2. Analyze spending patterns
3. Suggest savings alternatives (subway, coupons, etc.)
4. Provide relevant coupon codes from all_coupons.json

## Implementation Steps

### 1. Frontend (ChatInterface.tsx)
- Detect @ mentions in user input
- Highlight @ mentions in the UI
- Send tagged merchants to backend

### 2. Backend (main.py & agents)
- Parse @ mentions from messages
- Query processed_transactions.json for merchant data
- Search all_coupons.json for relevant coupons
- Generate savings suggestions

### 3. Response Format
```json
{
  "response": "Analysis text with savings suggestions",
  "merchant_data": {
    "merchant": "Uber",
    "total_spent": 245.50,
    "transaction_count": 12,
    "avg_per_transaction": 20.46
  },
  "savings_suggestions": [
    {
      "type": "alternative",
      "suggestion": "Take the subway instead",
      "estimated_savings": "$15 per trip"
    },
    {
      "type": "coupon",
      "merchant": "Uber",
      "code": "SAVE20NOW",
      "description": "$20 off your first order of $30 or more"
    }
  ]
}
```

## Files to Modify
1. `components/ChatInterface.tsx` - Add @ mention detection
2. `backend/main.py` - Add @ mention parsing endpoint
3. `backend/agents/mark_agent.py` - Add transaction analysis logic
4. `backend/agents/bounty_hunter_1.py` - Add coupon search by merchant
