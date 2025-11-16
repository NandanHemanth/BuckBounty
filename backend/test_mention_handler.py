"""
Test script to debug @ mention handler and check what merchants are available
"""

from vector_db import VectorDB
from mention_handler import MentionHandler

# Initialize vector DB
print("🔍 Initializing Vector Database...")
vector_db = VectorDB()

print(f"\n📊 Vector DB Stats:")
print(f"   Total transactions: {vector_db.index.ntotal}")
print(f"   Metadata entries: {len(vector_db.metadata)}")

# Show sample merchants
if vector_db.metadata:
    print(f"\n🏪 Sample Merchants (first 20):")
    merchants = set()
    for tx in vector_db.metadata[:50]:
        merchant = tx.get('merchant', 'Unknown')
        if merchant and merchant != 'Unknown':
            merchants.add(merchant)
    
    for i, merchant in enumerate(sorted(merchants)[:20], 1):
        print(f"   {i}. {merchant}")
    
    print(f"\n   Total unique merchants: {len(merchants)}")
    
    # Test mention handler
    print(f"\n🧪 Testing Mention Handler...")
    handler = MentionHandler(vector_db=vector_db)
    
    # Test with a real merchant
    if merchants:
        test_merchant = list(merchants)[0]
        print(f"\n   Testing with: @{test_merchant}")
        
        result = handler.process_mentions(f"How much did I spend on @{test_merchant}?")
        
        if result.get('has_mentions'):
            for mention in result.get('mentions', []):
                spending = mention.get('spending_analysis', {})
                print(f"\n   ✅ Found {spending.get('transaction_count', 0)} transactions")
                print(f"   💰 Total: ${spending.get('total_spent', 0)}")
                print(f"   📊 Average: ${spending.get('avg_per_transaction', 0)}")
                
                coupons = mention.get('coupons', [])
                if coupons:
                    print(f"   🎟️  Coupons: {len(coupons)}")
                
                suggestions = mention.get('savings_suggestions', [])
                if suggestions:
                    print(f"   💡 Suggestions: {len(suggestions)}")
    
    # Test with Uber specifically
    print(f"\n🚗 Testing with @Uber...")
    uber_result = handler.process_mentions("How much on @Uber?")
    
    if uber_result.get('has_mentions'):
        for mention in uber_result.get('mentions', []):
            spending = mention.get('spending_analysis', {})
            print(f"   Transactions: {spending.get('transaction_count', 0)}")
            print(f"   Total: ${spending.get('total_spent', 0)}")
            print(f"   Message: {spending.get('message', 'N/A')}")
    else:
        print("   ❌ No Uber transactions found")
        
        # Check if any merchant contains "uber"
        uber_merchants = [m for m in merchants if 'uber' in m.lower()]
        if uber_merchants:
            print(f"   💡 Found similar merchants: {uber_merchants}")
        else:
            print("   💡 No merchants containing 'uber' found")

else:
    print("\n❌ No transactions in vector database!")
    print("\n💡 To add transactions:")
    print("   1. Link a Plaid account via the frontend")
    print("   2. Or run: python backend/load_sample_transactions.py")

print("\n" + "="*60)
