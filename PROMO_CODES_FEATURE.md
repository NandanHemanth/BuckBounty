# 🎟️ @Codes Feature - Promo Code Lookup

## 🎯 Overview

Users can now type `@Codes` to instantly retrieve promo codes from the database, along with smart alternative savings suggestions!

## 📊 How It Works

### Usage 1: Get All Codes
**User types:** `@Codes`

**MARK shows:**
- All available promo codes
- Organized by merchant
- Top 2 codes per merchant
- Suggestion to ask for specific merchant

**Example Response:**
```
🎟️ Here are all available promo codes!

**Uber** (1 code):
  • RIDE10: $10 off your next 3 rides
  
**UberEats** (2 codes):
  • SAVE20NOW: $20 off your first order of $30 or more
  • FREESHIP: Free delivery on orders over $15

**DoorDash** (2 codes):
  • DASH25OFF: $25 off orders of $40+
  • DASHPASS30: 30 days free DashPass membership

... (and more)

💡 Want codes for a specific merchant? Just ask "@Codes Uber" or "@Codes Amazon"!
```

### Usage 2: Get Specific Merchant Codes
**User types:** `@Codes Uber`

**MARK shows:**
- All Uber promo codes
- Detailed information (code, description, expiry, discount)
- Alternative savings tip (e.g., use public transport)

**Example Response:**
```
🚗 PROMO CODES FOR UBER

Code: RIDE10
Description: $10 off your next 3 rides
Details: Valid for new Uber users. Maximum $10 off per ride.
Expires: 2025-12-31
Discount: $10
---

💡 ALTERNATIVE SAVINGS TIP:
Consider using public transportation! 🚇
- Monthly bus/metro pass: ~$80-120 (vs $200+ on rideshares)
- Bike sharing: ~$15/month
- Walking for short distances: FREE + healthy!

Save even more by combining promo codes with public transport for longer trips!
```

## 🎯 Supported Merchants

From `backend/data/coupons/all_coupons.json`:

### Food Delivery
- **UberEats**: SAVE20NOW, FREESHIP
- **DoorDash**: DASH25OFF, DASHPASS30
- **GrubHub**: GRUB15

### Shopping
- **Amazon**: PRIME20
- **Target**: TARGET10
- **Walmart**: SAVE15

### Transportation
- **Uber**: RIDE10
- **Lyft**: LYFT20

### Sports & Fitness
- **Adidas**: SPORT30, ADICLUB25
- **Nike**: NIKE20
- **Gymshark**: GAINS15

### Groceries
- **Instacart**: INSTA30
- **Whole Foods**: PRIME10

### Entertainment
- **Spotify**: MUSIC3FREE
- **Netflix**: STREAM30

### Travel
- **Airbnb**: TRAVEL55
- **Expedia**: HOTEL20

### Fashion
- **H&M**: FASHION15
- **Zara**: ZARA20

### Electronics
- **Best Buy**: TECH50
- **Newegg**: TECH15

### Health & Beauty
- **Sephora**: BEAUTY20
- **CVS**: HEALTH10

### Home & Garden
- **Home Depot**: HOME25
- **IKEA**: IKEA15

## 💡 Smart Alternative Suggestions

MARK provides category-specific alternative savings tips:

### Transportation
```
Consider using public transportation! 🚇
- Monthly bus/metro pass: ~$80-120 (vs $200+ on rideshares)
- Bike sharing: ~$15/month
- Walking for short distances: FREE + healthy!
```

### Food Delivery
```
Save even more by:
- Picking up orders yourself (save delivery fees)
- Cooking at home 3x/week (save $150+/month)
- Meal prepping on Sundays
```

### Shopping
```
Maximize savings by:
- Using cashback credit cards (1-5% back)
- Shopping during sales events
- Comparing prices across stores
```

### Entertainment
```
Consider:
- Sharing subscriptions with family (split costs)
- Free alternatives (library, YouTube, podcasts)
- Rotating subscriptions monthly
```

## 🔧 Technical Implementation

### Intent Detection
```python
if "@codes" in message_lower or "@code" in message_lower:
    return "promo_codes"
```

### Handler Logic
```python
async def _handle_promo_codes(user_id, message):
    # 1. Load all_coupons.json
    # 2. Extract merchant from message
    # 3. If no merchant: show all codes
    # 4. If merchant specified: show specific codes + alternatives
    # 5. Generate response with LLM
```

### Data Structure
```json
{
  "id": "uber_001",
  "merchant": "Uber",
  "code": "RIDE10",
  "description": "$10 off your next 3 rides",
  "details": "Valid for new Uber users...",
  "expiry_date": "2025-12-31",
  "category": "transportation",
  "discount_type": "fixed",
  "discount_value": 10
}
```

## 🎯 Example Queries

### Query 1: All Codes
```
User: @Codes
MARK: Shows all 28 promo codes organized by merchant
```

### Query 2: Uber Codes
```
User: @Codes Uber
MARK: Shows Uber codes + public transport alternative
```

### Query 3: Food Delivery
```
User: @Codes UberEats
MARK: Shows UberEats codes + cooking at home tip
```

### Query 4: Shopping
```
User: @Codes Amazon
MARK: Shows Amazon codes + cashback card suggestion
```

### Query 5: Entertainment
```
User: @Codes Spotify
MARK: Shows Spotify codes + subscription sharing tip
```

## ✅ Benefits

### For Users:
- **Instant Access** - No need to search for codes
- **Comprehensive** - All codes in one place
- **Smart Alternatives** - Learn better ways to save
- **Detailed Info** - Expiry dates, terms, discount amounts
- **Easy to Use** - Just type @Codes

### For Platform:
- **Engagement** - Users come back for codes
- **Value** - Practical, immediate savings
- **Education** - Teaches smart spending habits
- **Differentiation** - Unique @Codes feature
- **Trust** - Shows we help users save money

## 🚀 Testing

### Test 1: All Codes
1. Type: `@Codes`
2. Should see: All merchants with codes
3. Should include: Suggestion to ask for specific merchant

### Test 2: Specific Merchant
1. Type: `@Codes Uber`
2. Should see: All Uber codes with details
3. Should include: Public transport alternative

### Test 3: Category Search
1. Type: `@Codes transportation`
2. Should see: Uber and Lyft codes
3. Should include: Alternative savings tips

### Test 4: Case Insensitive
1. Type: `@codes uber` (lowercase)
2. Should work: Same as @Codes Uber
3. Should include: All features

## 🎊 Result

**Users can now:**
- Get instant promo codes with `@Codes`
- Search specific merchants: `@Codes Uber`
- Learn alternative savings methods
- See detailed code information
- Save money immediately

**The @Codes feature makes MARK a one-stop shop for savings!** 🎟️💰✨

---

**Status:** ✅ Complete & Production Ready  
**Data Source:** backend/data/coupons/all_coupons.json  
**Merchants:** 28 codes across 20+ merchants  
**Categories:** 11 categories with alternatives  
**User Experience:** Instant, helpful, educational
