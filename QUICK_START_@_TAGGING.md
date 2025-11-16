# @ Tagging Quick Start Guide

## TL;DR
Tag any merchant with @ (e.g., `@Uber`, `@Starbucks`) and MARK will analyze your spending and suggest ways to save money.

## Usage Examples

### Example 1: Check Spending
```
You: "How much did I spend on @Uber last month?"

MARK: "You spent $245.50 on Uber across 12 trips (avg $20.46/trip).
      
      💰 Coupons: SAVE20NOW - $20 off orders $30+
      💡 Save money: Take the subway instead (Save $10-15/trip)"
```

### Example 2: Compare Merchants
```
You: "Compare my @Uber vs @Lyft spending"

MARK: "Uber: $245.50 (12 trips)
       Lyft: $180.30 (8 trips)
       
       You're spending more on Uber. Consider using Lyft more often!"
```

### Example 3: Find Deals
```
You: "Show me @Starbucks coupons"

MARK: "💰 Available Starbucks Coupons:
       - COFFEE10: $10 off $20+
       - FREEBREW: Free drink with purchase
       
       💡 Save $100-150/month by brewing coffee at home!"
```

## How It Works

1. **Type @ + merchant name** in your message
2. **@ mention turns green** (visual confirmation)
3. **MARK analyzes** your transaction data
4. **Get personalized response** with:
   - Spending breakdown
   - Available coupons
   - Money-saving alternatives

## Supported Merchant Types

- 🚗 **Ride Services**: Uber, Lyft, taxi
- ☕ **Coffee Shops**: Starbucks, Dunkin, local cafes
- 🍔 **Food Delivery**: DoorDash, UberEats, GrubHub
- 🛒 **Shopping**: Amazon, Target, Walmart
- 🏪 **Retail**: Any store in your transactions

## What You Get

### Transaction Analysis
- Total amount spent
- Number of transactions
- Average per transaction
- Last 30 days spending
- Date range

### Coupon Codes
- Active, non-expired coupons
- Discount amount
- Expiry date
- Usage instructions

### Savings Suggestions
- Alternative options (subway, bike, home cooking)
- Estimated savings per month
- Environmental/health benefits
- Practical tips

## Troubleshooting

### "No transactions found"
**Reasons:**
- Accounts not linked yet
- Haven't used that merchant recently
- Merchant name doesn't match exactly

**Solutions:**
- Link your bank accounts
- Try variations (@Uber, @UberEats, @UberTechnologies)
- Check available merchants in your data

### @ mention not highlighted
**Solutions:**
- Refresh the page
- Check browser console for errors
- Make sure frontend is running

### No coupons showing
**Reasons:**
- No coupons available for that merchant
- All coupons expired
- Merchant name mismatch

**Solutions:**
- Try related merchants (@UberEats instead of @Uber)
- Check `backend/data/coupons/all_coupons.json`

## Pro Tips

1. **Be specific**: `@UberEats` vs `@Uber` may give different results
2. **Try variations**: `@Starbucks`, `@StarBucks`, `@starbucks` all work
3. **Multiple mentions**: Tag multiple merchants to compare
4. **Ask follow-ups**: "Show me more @Uber alternatives"
5. **Check regularly**: New coupons added frequently

## Common Queries

```
✅ "How much on @Uber last month?"
✅ "@Starbucks spending analysis"
✅ "Show me @DoorDash coupons"
✅ "Compare @Uber and @Lyft"
✅ "Find @Amazon deals"
✅ "@Target vs @Walmart spending"
✅ "Best @Starbucks alternatives"
```

## What's Next?

After getting your analysis, you can:
1. **Apply coupons** - Use the codes provided
2. **Try alternatives** - Follow the savings suggestions
3. **Track progress** - Ask again next month to compare
4. **Link more accounts** - Get complete spending picture
5. **Set budgets** - Ask MARK to help you budget

## Need Help?

- Check `TESTING_@_TAGGING.md` for detailed testing guide
- See `@_TAGGING_FIXED.md` for technical details
- Ask MARK: "How do I use @ mentions?"

---

**Start saving money today! Just type @ and tag any merchant.** 💰
