"""
Quick script to clear Redis cache for testing
"""
import redis

try:
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Clear all cache keys
    keys = r.keys('chat_response:*')
    if keys:
        r.delete(*keys)
        print(f"✅ Cleared {len(keys)} cached responses")
    else:
        print("ℹ️ No cached responses found")
    
    # Also clear savings analysis cache
    savings_keys = r.keys('savings_analysis:*')
    if savings_keys:
        r.delete(*savings_keys)
        print(f"✅ Cleared {len(savings_keys)} savings analysis cache")
    
    print("\n🎉 Cache cleared! Try the Budget? button again.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure Redis is running!")
