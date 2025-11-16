# @ Tagging Feature - Complete Implementation

## Overview
Users can now tag merchants with "@" (e.g., "@Uber", "@Starbucks") and MARK will automatically:
1. Access transaction data for that merchant
2. Analyze spending patterns
3. Provide relevant coupon codes
4. Suggest money-saving alternatives

## How It Works

### User Experience
1. Type a message with @ mentions: "How much did I spend on @Uber last month?"
2. @ mentions are highlighted in green in the chat
3. MARK responds with:
   - Transaction analysis (total spent, number of transactions, monthly average)
   - Available coupon codes from the database
   - Alternative savings suggestions (e.g., "Take the subway instead")

### Example Queries
- "How much did I spend on @Uber last month?"
- "Show me @Starbucks spending and coupons"
- "Compare my @DoorDash vs @UberEats spending"
- "Find me @Amazon deals"

### Savings Suggestions by Category

#### Ride Services (@Uber, @Lyft)
- Public transportation alternatives
- Bike-sharing options
- Estimated savings per trip
- Environmental benefits

#### Coffee Shops (@Starbucks, @Dunkin)
- Home brewing suggestions
- Monthly savings calculations
- Equipment recommendations

#### Food Delivery (@DoorDash, @UberEats, @GrubHub)
- Meal prep alternatives
- Pickup vs delivery savings
- Batch cooking tips

#### Shopping (@Amazon, retail)
- Wait for sales events
- Buy used/refurbished options
- Price tracking recommendations

## Technical Implementation

### Frontend (components/ChatInterface.tsx)
- Detects @ mentions using regex: `/@(\w+)/g`
- Highlights mentions with green background
- Displays them as: `@Merchant`

### Backend (backend/mention_handler.py)
- `MentionHandler` class processes @ mentions
- Loads transaction data from `processed_transactions.json`
- Loads coupons from `coupons/all_coupons.json`
- Generates contextual savings suggestions

### API Integration (backend/main.py)
- `/api/agents/chat` endpoint enhanced
- Detects @ mentions before routing to agents
- Enriches message with merchant analysis
- Returns structured data with coupons and suggestions

## Response Format

```json
{
  "response": "You spent $245.50 on Uber last month across 12 trips...",
  "mention_data": {
    "has_mentions": true,
    "mentions": [
      {
        "merchant": "uber",
        "spending_analysis": {
          "total_spent": 245.50,
          "transaction_count": 12,
          "monthly_average": 245.50
        },
        "coupons": [
          {
            "code": "SAVE20NOW",
            "description": "$20 off your first order of $30 or more",
            "merchant": "UberEats"
          }
        ],
        "savings_suggestions": [
          {
            "type": "alternative",
            "title": "Public Transportation",
            "suggestion": "Consider taking the subway or bus instead",
            "estimated_savings": "$10-15 per trip"
          }
        ]
      }
    ]
  }
}
```

## Files Modified

1. **components/ChatInterface.tsx**
   - Added @ mention detection and highlighting
   - Enhanced message rendering with regex parsing

2. **backend/mention_handler.py** (NEW)
   - Complete mention processing logic
   - Transaction analysis
   - Coupon matching
   - Savings suggestion generation

3. **backend/main.py**
   - Integrated mention_handler
   - Enhanced chat endpoint
   - Added mention data to responses

## Future Enhancements

1. **Smart Merchant Matching**
   - Fuzzy matching for merchant names
   - Handle variations (e.g., "uber" vs "uber eats")

2. **Transaction Data Integration**
   - Connect to actual transaction database
   - Real-time spending calculations
   - Historical trend analysis

3. **Personalized Suggestions**
   - Learn user preferences
   - Location-based alternatives
   - Seasonal recommendations

4. **Coupon Expiry Alerts**
   - Notify users of expiring coupons
   - Auto-apply best available coupons
   - Track coupon usage

## Testing

### Test Queries
```
1. "How much did I spend on @Uber last month?"
2. "@Starbucks spending analysis"
3. "Show me @DoorDash coupons"
4. "Compare @Uber and @Lyft costs"
5. "Find @Amazon deals for electronics"
```

### Expected Behavior
- @ mentions highlighted in green
- Spending analysis displayed
- Relevant coupons listed
- Alternative suggestions provided
- Estimated savings calculated

## Notes
- Coupon data loaded from `backend/data/coupons/all_coupons.json`
- Transaction data from `backend/data/processed_transactions.json`
- Case-insensitive merchant matching
- Expired coupons automatically filtered out
