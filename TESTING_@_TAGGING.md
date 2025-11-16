# Testing @ Tagging Feature

## Quick Test Guide

### Prerequisites
1. Backend server running: `python backend/main.py`
2. Frontend running: `npm run dev`
3. At least some transactions loaded in the vector database

### Test Scenarios

#### Test 1: Basic @ Mention
**Input:** `How much did I spend on @Uber last month?`

**Expected Output:**
- @ mention highlighted in green in the UI
- MARK responds with:
  - Transaction count and total spent (if found)
  - OR message about no transactions found
  - Available Uber coupons
  - Alternative suggestions (subway, bike-sharing)

#### Test 2: Multiple @ Mentions
**Input:** `Compare my spending on @Uber vs @Lyft`

**Expected Output:**
- Both mentions highlighted
- Analysis for each merchant
- Comparative insights
- Relevant coupons for both

#### Test 3: Coffee Shop
**Input:** `Show me my @Starbucks spending`

**Expected Output:**
- Transaction analysis
- Starbucks coupons (if available)
- Home brewing suggestions
- Monthly savings calculations

#### Test 4: Food Delivery
**Input:** `@DoorDash spending analysis`

**Expected Output:**
- Transaction breakdown
- DoorDash coupons
- Meal prep alternatives
- Pickup vs delivery savings

#### Test 5: No Transactions Found
**Input:** `How much did I spend on @RandomMerchant?`

**Expected Output:**
- Message: "No transactions found for RandomMerchant"
- Suggestion to link accounts
- General coupons (if available)
- Alternative suggestions based on merchant type

## Debugging

### Check Vector Database
```python
# In Python console
from vector_db import VectorDB
db = VectorDB()
print(f"Total transactions: {db.index.ntotal}")
print(f"Sample transactions: {db.metadata[:5]}")
```

### Check Merchant Names
```python
# See what merchants are in the database
from vector_db import VectorDB
db = VectorDB()
merchants = set(tx.get('merchant', '') for tx in db.metadata)
print(f"Available merchants: {sorted(merchants)}")
```

### Test Mention Handler Directly
```python
from mention_handler import MentionHandler
from vector_db import VectorDB

db = VectorDB()
handler = MentionHandler(vector_db=db)

# Test extraction
mentions = handler.extract_mentions("How much on @Uber and @Starbucks?")
print(f"Extracted mentions: {mentions}")

# Test full processing
result = handler.process_mentions("Show me @Uber spending")
print(result)
```

## Common Issues & Solutions

### Issue 1: No Transactions Found
**Cause:** Vector database is empty or merchant name doesn't match
**Solution:**
1. Check if transactions are loaded: `db.index.ntotal`
2. Check merchant names in database
3. Try partial matches (e.g., @Uber might match "Uber Technologies")

### Issue 2: @ Mentions Not Highlighted
**Cause:** Frontend regex not matching
**Solution:**
- Check browser console for errors
- Verify ChatInterface.tsx changes applied
- Try refreshing the page

### Issue 3: Backend Error
**Cause:** Vector DB not initialized or import error
**Solution:**
```bash
# Check backend logs
# Verify vector_db is initialized in main.py
# Check mention_handler.py imports
```

### Issue 4: Coupons Not Showing
**Cause:** Coupon file not found or merchant name mismatch
**Solution:**
1. Verify `backend/data/coupons/all_coupons.json` exists
2. Check merchant names in coupon file match @ mentions
3. Check coupon expiry dates

## Expected Behavior Summary

### When Transactions Found:
```
You spent $245.50 on Uber last month across 12 trips (avg $20.46/trip).

💰 Available Coupons (2):
- SAVE20NOW: $20 off orders $30+ (Expires: 2026-01-10)
- FREESHIP: Free delivery on orders over $15 (Expires: 2025-11-18)

💡 Savings Suggestions:
- Public Transportation: Consider taking the subway or bus instead (Save: $10-15 per trip)
- Bike Share: Use bike-sharing services for short distances (Save: $5-10 per trip)
```

### When No Transactions Found:
```
I don't see any transactions for RandomMerchant in your linked accounts. This could mean:
- You haven't used this merchant recently
- Your accounts aren't linked yet
- The merchant name might be different in your transactions

Would you like to:
1. Link your accounts to see transaction history
2. Try a different merchant name
3. See available coupons for this merchant anyway

💰 Available Coupons (if any)
💡 General Savings Suggestions
```

## Performance Notes

- First query may be slower (loading models)
- Subsequent queries should be fast (<1s)
- Vector search limited to 100 results for performance
- Coupon matching is case-insensitive

## Next Steps After Testing

1. **Add More Merchants:** Update savings suggestions for more merchant types
2. **Improve Matching:** Add fuzzy matching for merchant names
3. **Cache Results:** Cache merchant analysis for faster responses
4. **Add Analytics:** Track which merchants users query most
5. **Personalization:** Learn user preferences over time
