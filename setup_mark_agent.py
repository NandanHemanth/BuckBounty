"""
Setup script for MARK Agent enhanced features
Initializes Redis, RAG indices, and verifies all components
"""

import os
import sys
from pathlib import Path

def check_redis():
    """Check if Redis is available"""
    print("🔍 Checking Redis connection...")
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis is running and accessible")
        return True
    except ImportError:
        print("❌ Redis library not installed. Run: pip install redis")
        return False
    except Exception as e:
        print(f"⚠️ Redis not available: {e}")
        print("   Install Redis:")
        print("   - Windows: https://redis.io/download")
        print("   - Mac: brew install redis")
        print("   - Linux: sudo apt-get install redis-server")
        print("\n   Then start Redis: redis-server")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required = [
        'fastapi',
        'redis',
        'faiss',
        'numpy',
        'google.generativeai',
        'httpx',
        'beautifulsoup4'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r backend/requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'data/rag',
        'data/coupons',
        'data/finance_news',
        'data/vector_db'
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
    
    print("✅ All directories created")

def check_env_variables():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'OPENROUTER_API_KEY': 'OpenRouter API key for Claude',
        'GEMINI_API_KEY': 'Gemini API key for fallback and embeddings'
    }
    
    optional_vars = {
        'REDIS_URL': 'Redis connection URL (default: redis://localhost:6379)',
        'PLAID_CLIENT_ID': 'Plaid API for banking data',
        'STRIPE_API_KEY': 'Stripe API for payments'
    }
    
    missing_required = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:10]}...")
        else:
            print(f"❌ {var}: Not set ({description})")
            missing_required.append(var)
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"⚠️ {var}: Not set ({description})")
    
    if missing_required:
        print(f"\n❌ Missing required variables: {', '.join(missing_required)}")
        print("   Add them to your .env file")
        return False
    
    print("✅ All required environment variables set")
    return True

def initialize_rag_service():
    """Initialize RAG service"""
    print("\n🔧 Initializing RAG service...")
    
    try:
        sys.path.append('backend')
        from rag_service import rag_service
        
        stats = rag_service.get_stats()
        print(f"✅ FLAT index: {stats['flat_index']['total_vectors']} vectors")
        print(f"✅ HNSW index: {stats['hnsw_index']['total_vectors']} vectors")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing RAG service: {e}")
        return False

def initialize_redis_cache():
    """Initialize Redis cache"""
    print("\n🔧 Initializing Redis cache...")
    
    try:
        sys.path.append('backend')
        from redis_cache import redis_cache
        
        if redis_cache.enabled:
            print("✅ Redis cache initialized")
            
            # Test cache operations
            redis_cache.set_agent_status("test", "Ready")
            status = redis_cache.get_agent_status("test")
            
            if status == "Ready":
                print("✅ Cache operations working")
            
            return True
        else:
            print("⚠️ Redis cache disabled (running without cache)")
            return True
    except Exception as e:
        print(f"❌ Error initializing Redis cache: {e}")
        return False

def verify_credit_cards():
    """Verify credit card data is available"""
    print("\n🔍 Checking credit card data...")
    
    try:
        import json
        with open('credit_cards.json', 'r') as f:
            data = json.load(f)
            cards = data.get('credit_cards', [])
            print(f"✅ Loaded {len(cards)} credit cards")
            return True
    except Exception as e:
        print(f"❌ Error loading credit cards: {e}")
        return False

def main():
    """Run all setup checks"""
    print("=" * 60)
    print("🚀 MARK Agent Enhanced Setup")
    print("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_env_variables),
        ("Directories", lambda: (create_directories(), True)[1]),
        ("Redis Connection", check_redis),
        ("Credit Card Data", verify_credit_cards),
        ("RAG Service", initialize_rag_service),
        ("Redis Cache", initialize_redis_cache)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Setup Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All checks passed! MARK Agent is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Start Redis: redis-server")
        print("   2. Start backend: cd backend && uvicorn main:app --reload")
        print("   3. Start frontend: npm run dev")
        print("   4. Open http://localhost:3000")
    else:
        print("\n⚠️ Some checks failed. Please fix the issues above.")
        print("   Refer to MARK_AGENT_IMPLEMENTATION.md for detailed setup instructions.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
