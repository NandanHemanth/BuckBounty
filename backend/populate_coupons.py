"""
Populate BountyHunter1 with realistic coupon data
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import random

# Create data directory
data_dir = Path("./data/coupons")
data_dir.mkdir(parents=True, exist_ok=True)

# Generate expiry dates (1-60 days from now)
def random_expiry():
    days = random.randint(1, 60)
    return (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

# Coupon data organized by category
coupons_data = [
    # FOOD DELIVERY (Dining category)
    {
        "id": "ubereats_001",
        "source": "manual",
        "merchant": "UberEats",
        "code": "SAVE20NOW",
        "description": "$20 off your first order of $30 or more",
        "details": "Valid for new users only. Minimum order $30. Delivery fees may apply.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "food_delivery",
        "discount_type": "fixed",
        "discount_value": 20
    },
    {
        "id": "ubereats_002",
        "source": "manual",
        "merchant": "UberEats",
        "code": "FREESHIP",
        "description": "Free delivery on orders over $15",
        "details": "No minimum order required. Valid on all restaurants.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "food_delivery",
        "discount_type": "free_shipping",
        "discount_value": 0
    },
    {
        "id": "doordash_001",
        "source": "manual",
        "merchant": "DoorDash",
        "code": "DASH25OFF",
        "description": "$25 off orders of $40+",
        "details": "Valid for first-time DoorDash users. Minimum order $40.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "food_delivery",
        "discount_type": "fixed",
        "discount_value": 25
    },
    {
        "id": "doordash_002",
        "source": "manual",
        "merchant": "DoorDash",
        "code": "DASHPASS30",
        "description": "30 days free DashPass membership",
        "details": "Enjoy $0 delivery fees and reduced service fees. Cancel anytime.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "food_delivery",
        "discount_type": "subscription",
        "discount_value": 0
    },
    {
        "id": "grubhub_001",
        "source": "manual",
        "merchant": "GrubHub",
        "code": "GRUB15",
        "description": "$15 off your order",
        "details": "Minimum order $30. Valid on participating restaurants.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "food_delivery",
        "discount_type": "fixed",
        "discount_value": 15
    },

    # SHOPPING (General Retail)
    {
        "id": "amazon_001",
        "source": "manual",
        "merchant": "Amazon",
        "code": "PRIME20",
        "description": "20% off select items with Prime",
        "details": "Valid on items marked 'Prime Exclusive Deal'. Maximum discount $50.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "shopping",
        "discount_type": "percentage",
        "discount_value": 20
    },
    {
        "id": "target_001",
        "source": "manual",
        "merchant": "Target",
        "code": "TARGET10",
        "description": "10% off entire purchase",
        "details": "Valid in-store and online. Excludes gift cards and alcohol.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "shopping",
        "discount_type": "percentage",
        "discount_value": 10
    },
    {
        "id": "walmart_001",
        "source": "manual",
        "merchant": "Walmart",
        "code": "SAVE15",
        "description": "$15 off orders of $50+",
        "details": "Valid on Walmart.com. Free shipping on orders over $35.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "shopping",
        "discount_type": "fixed",
        "discount_value": 15
    },

    # SPORTS & FITNESS (Recreation)
    {
        "id": "adidas_001",
        "source": "manual",
        "merchant": "Adidas",
        "code": "SPORT30",
        "description": "30% off sitewide",
        "details": "Valid on full-price items. Excludes Yeezy and limited editions.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "sports",
        "discount_type": "percentage",
        "discount_value": 30
    },
    {
        "id": "adidas_002",
        "source": "manual",
        "merchant": "Adidas",
        "code": "ADICLUB25",
        "description": "Extra 25% off sale items",
        "details": "Join adiClub for free and get exclusive member pricing.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "sports",
        "discount_type": "percentage",
        "discount_value": 25
    },
    {
        "id": "nike_001",
        "source": "manual",
        "merchant": "Nike",
        "code": "NIKE20",
        "description": "20% off your first order",
        "details": "Sign up for Nike Membership and get 20% off. Free shipping on all orders.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "sports",
        "discount_type": "percentage",
        "discount_value": 20
    },
    {
        "id": "gymshark_001",
        "source": "manual",
        "merchant": "Gymshark",
        "code": "GAINS15",
        "description": "15% off all workout gear",
        "details": "Valid on all collections. Free shipping over $75.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "sports",
        "discount_type": "percentage",
        "discount_value": 15
    },

    # TRANSPORTATION (Uber, Lyft)
    {
        "id": "uber_001",
        "source": "manual",
        "merchant": "Uber",
        "code": "RIDE10",
        "description": "$10 off your next 3 rides",
        "details": "Valid for new Uber users. Maximum $10 off per ride.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "transportation",
        "discount_type": "fixed",
        "discount_value": 10
    },
    {
        "id": "lyft_001",
        "source": "manual",
        "merchant": "Lyft",
        "code": "LYFT20",
        "description": "$20 in ride credits",
        "details": "Split across your first 4 rides. New users only.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "transportation",
        "discount_type": "fixed",
        "discount_value": 20
    },

    # GROCERIES
    {
        "id": "instacart_001",
        "source": "manual",
        "merchant": "Instacart",
        "code": "INSTA30",
        "description": "$30 off your first order",
        "details": "Minimum order $100. Free delivery on first order.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "groceries",
        "discount_type": "fixed",
        "discount_value": 30
    },
    {
        "id": "wholefood_001",
        "source": "manual",
        "merchant": "Whole Foods",
        "code": "PRIME10",
        "description": "Extra 10% off for Prime members",
        "details": "Valid on sale items. Show Prime membership at checkout.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "groceries",
        "discount_type": "percentage",
        "discount_value": 10
    },

    # ENTERTAINMENT
    {
        "id": "spotify_001",
        "source": "manual",
        "merchant": "Spotify",
        "code": "MUSIC3FREE",
        "description": "3 months Premium for free",
        "details": "New subscribers only. Cancel anytime. Auto-renews at $10.99/month.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "entertainment",
        "discount_type": "subscription",
        "discount_value": 0
    },
    {
        "id": "netflix_001",
        "source": "manual",
        "merchant": "Netflix",
        "code": "STREAM30",
        "description": "30 days free trial",
        "details": "Watch unlimited movies and TV shows. Cancel anytime.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "entertainment",
        "discount_type": "subscription",
        "discount_value": 0
    },

    # TRAVEL
    {
        "id": "airbnb_001",
        "source": "manual",
        "merchant": "Airbnb",
        "code": "TRAVEL55",
        "description": "$55 off your first booking",
        "details": "Minimum booking $150. Valid for new Airbnb users.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "travel",
        "discount_type": "fixed",
        "discount_value": 55
    },
    {
        "id": "expedia_001",
        "source": "manual",
        "merchant": "Expedia",
        "code": "HOTEL20",
        "description": "20% off hotel bookings",
        "details": "Valid on select hotels. Book by end of month.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "travel",
        "discount_type": "percentage",
        "discount_value": 20
    },

    # FASHION
    {
        "id": "hm_001",
        "source": "manual",
        "merchant": "H&M",
        "code": "FASHION15",
        "description": "15% off your purchase",
        "details": "Valid in-store and online. Excludes sale items.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "fashion",
        "discount_type": "percentage",
        "discount_value": 15
    },
    {
        "id": "zara_001",
        "source": "manual",
        "merchant": "Zara",
        "code": "ZARA20",
        "description": "20% off new arrivals",
        "details": "Valid on full-price items. Free shipping over $50.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "fashion",
        "discount_type": "percentage",
        "discount_value": 20
    },

    # ELECTRONICS
    {
        "id": "bestbuy_001",
        "source": "manual",
        "merchant": "Best Buy",
        "code": "TECH50",
        "description": "$50 off purchases of $500+",
        "details": "Valid on select electronics. Excludes Apple products.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "electronics",
        "discount_type": "fixed",
        "discount_value": 50
    },
    {
        "id": "newegg_001",
        "source": "manual",
        "merchant": "Newegg",
        "code": "TECH15",
        "description": "15% off computer components",
        "details": "Valid on CPUs, GPUs, and motherboards. Maximum discount $100.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "electronics",
        "discount_type": "percentage",
        "discount_value": 15
    },

    # HEALTH & BEAUTY
    {
        "id": "sephora_001",
        "source": "manual",
        "merchant": "Sephora",
        "code": "BEAUTY20",
        "description": "20% off for Beauty Insider members",
        "details": "Join for free. Valid on all brands. Free shipping.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "health_beauty",
        "discount_type": "percentage",
        "discount_value": 20
    },
    {
        "id": "cvs_001",
        "source": "manual",
        "merchant": "CVS",
        "code": "HEALTH10",
        "description": "$10 off $50 purchase",
        "details": "Valid on health and wellness products. ExtraCare members only.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "health_beauty",
        "discount_type": "fixed",
        "discount_value": 10
    },

    # HOME & GARDEN
    {
        "id": "homedepot_001",
        "source": "manual",
        "merchant": "Home Depot",
        "code": "HOME25",
        "description": "$25 off orders of $200+",
        "details": "Valid on home improvement items. Excludes appliances.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "home_garden",
        "discount_type": "fixed",
        "discount_value": 25
    },
    {
        "id": "ikea_001",
        "source": "manual",
        "merchant": "IKEA",
        "code": "IKEA15",
        "description": "15% off furniture",
        "details": "Valid on select furniture collections. Free assembly with purchase.",
        "found_date": datetime.now().isoformat(),
        "expiry_date": random_expiry(),
        "category": "home_garden",
        "discount_type": "percentage",
        "discount_value": 15
    }
]

# Save to JSON file
coupon_file = data_dir / "all_coupons.json"

with open(coupon_file, 'w') as f:
    json.dump(coupons_data, f, indent=2)

print(f"✅ Successfully created {len(coupons_data)} coupons!")
print(f"📁 Saved to: {coupon_file}")
print(f"\nCoupon breakdown by category:")

# Count by category
from collections import Counter
categories = Counter(c['category'] for c in coupons_data)
for category, count in categories.most_common():
    print(f"  - {category}: {count} coupons")

print(f"\n🎯 Total merchants: {len(set(c['merchant'] for c in coupons_data))}")
print(f"💰 Total discount value: ${sum(c.get('discount_value', 0) for c in coupons_data)}")
