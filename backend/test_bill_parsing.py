"""
Test script for bill parsing with Gemini
"""
import os
from dotenv import load_dotenv
from bill_service import BillService

load_dotenv()

def test_bill_service():
    """Test if BillService initializes correctly"""
    try:
        service = BillService()
        print("✅ BillService initialized successfully")
        print(f"✅ Gemini API Key found: {os.getenv('GEMINI_API_KEY')[:10]}...")
        return True
    except Exception as e:
        print(f"❌ Error initializing BillService: {e}")
        return False

def test_with_sample_data():
    """Test parsing with mock data structure"""
    sample_bill = {
        "items": [
            {"name": "Burger", "quantity": 2, "price": 12.99},
            {"name": "Fries", "quantity": 1, "price": 4.99},
            {"name": "Soda", "quantity": 2, "price": 2.99}
        ],
        "subtotal": 36.95,
        "tax": 3.33,
        "tip": 7.00,
        "total": 47.28
    }
    
    print("\n📋 Sample Bill Structure:")
    print(f"Items: {len(sample_bill['items'])}")
    print(f"Subtotal: ${sample_bill['subtotal']:.2f}")
    print(f"Tax: ${sample_bill['tax']:.2f}")
    print(f"Tip: ${sample_bill['tip']:.2f}")
    print(f"Total: ${sample_bill['total']:.2f}")
    
    # Test split calculation
    service = BillService()
    
    # Select first 2 items, split by 2
    sample_bill['items'][0]['selected'] = True
    sample_bill['items'][0]['splitBy'] = 2
    sample_bill['items'][1]['selected'] = True
    sample_bill['items'][1]['splitBy'] = 1
    sample_bill['items'][2]['selected'] = False
    
    amount = service.calculate_split_amount(
        sample_bill['items'],
        sample_bill['tax'],
        sample_bill['tip']
    )
    
    print(f"\n💰 Your share (Burger/2 + Fries): ${amount:.2f}")
    return True

if __name__ == "__main__":
    print("🧪 Testing Bill Parsing Service\n")
    print("=" * 50)
    
    if test_bill_service():
        test_with_sample_data()
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("\n📝 To test with a real image:")
        print("   1. Start the backend: python main.py")
        print("   2. Start the frontend: npm run dev")
        print("   3. Click 'Split Bill' and upload a receipt")
    else:
        print("\n❌ Tests failed. Check your GEMINI_API_KEY in .env")
