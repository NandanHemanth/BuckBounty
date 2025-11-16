"""
Redis Cache Layer for BuckBounty
Stores chat history, agent responses, and current month transactions
"""

import redis
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class RedisCache:
    """Redis cache for chat history and transaction data"""

    def __init__(self):
        """Initialize Redis connection"""
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            print("✅ Redis cache connected")
        except Exception as e:
            print(f"⚠️ Redis not available: {e}. Running without cache.")
            self.enabled = False
            self.redis_client = None

    def cache_chat_response(self, user_id: str, query: str, response: str, metadata: Optional[Dict] = None):
        """Cache chat response for 24 hours"""
        if not self.enabled:
            return

        try:
            key = f"chat:{user_id}:{hash(query)}"
            data = {
                "query": query,
                "response": response,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Store for 24 hours
            self.redis_client.setex(
                key,
                timedelta(hours=24),
                json.dumps(data)
            )
            print(f"💾 Cached chat response for user {user_id}")
        except Exception as e:
            print(f"❌ Error caching chat: {e}")

    def get_cached_response(self, user_id: str, query: str) -> Optional[Dict]:
        """Get cached response if available"""
        if not self.enabled:
            return None

        try:
            key = f"chat:{user_id}:{hash(query)}"
            data = self.redis_client.get(key)
            
            if data:
                cached = json.loads(data)
                print(f"✅ Cache hit for user {user_id}")
                return cached
            
            return None
        except Exception as e:
            print(f"❌ Error retrieving cache: {e}")
            return None

    def cache_conversation_history(self, user_id: str, messages: List[Dict]):
        """Cache conversation history for 24 hours"""
        if not self.enabled:
            return

        try:
            key = f"conversation:{user_id}"
            self.redis_client.setex(
                key,
                timedelta(hours=24),
                json.dumps(messages, default=str)
            )
        except Exception as e:
            print(f"❌ Error caching conversation: {e}")

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Get cached conversation history"""
        if not self.enabled:
            return []

        try:
            key = f"conversation:{user_id}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else []
        except Exception as e:
            print(f"❌ Error retrieving conversation: {e}")
            return []

    def cache_current_month_transactions(self, user_id: str, transactions: List[Dict]):
        """Cache current month transactions"""
        if not self.enabled:
            return

        try:
            key = f"transactions:current:{user_id}"
            current_month = datetime.now().strftime('%Y-%m')
            
            data = {
                "month": current_month,
                "transactions": transactions,
                "cached_at": datetime.now().isoformat()
            }
            
            # Cache until end of month
            days_left = (datetime.now().replace(day=28) + timedelta(days=4)).replace(day=1) - datetime.now()
            
            self.redis_client.setex(
                key,
                days_left,
                json.dumps(data, default=str)
            )
            print(f"💾 Cached {len(transactions)} current month transactions")
        except Exception as e:
            print(f"❌ Error caching transactions: {e}")

    def get_current_month_transactions(self, user_id: str) -> Optional[List[Dict]]:
        """Get cached current month transactions"""
        if not self.enabled:
            return None

        try:
            key = f"transactions:current:{user_id}"
            data = self.redis_client.get(key)
            
            if data:
                cached = json.loads(data)
                # Verify it's still current month
                if cached.get('month') == datetime.now().strftime('%Y-%m'):
                    print(f"✅ Retrieved {len(cached['transactions'])} cached transactions")
                    return cached['transactions']
            
            return None
        except Exception as e:
            print(f"❌ Error retrieving cached transactions: {e}")
            return None

    def set_agent_status(self, agent_id: str, status: str):
        """Set agent status (Ready, Running, Error)"""
        if not self.enabled:
            return

        try:
            key = f"agent:status:{agent_id}"
            data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                key,
                timedelta(minutes=5),  # Status expires after 5 minutes
                json.dumps(data)
            )
        except Exception as e:
            print(f"❌ Error setting agent status: {e}")

    def get_agent_status(self, agent_id: str) -> str:
        """Get agent status"""
        if not self.enabled:
            return "Ready"

        try:
            key = f"agent:status:{agent_id}"
            data = self.redis_client.get(key)
            
            if data:
                status_data = json.loads(data)
                return status_data.get('status', 'Ready')
            
            return "Ready"
        except Exception as e:
            print(f"❌ Error getting agent status: {e}")
            return "Ready"

    def cache_savings_analysis(self, user_id: str, analysis: Dict):
        """Cache savings and investment analysis"""
        if not self.enabled:
            return

        try:
            key = f"savings:analysis:{user_id}"
            data = {
                "analysis": analysis,
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache for 6 hours
            self.redis_client.setex(
                key,
                timedelta(hours=6),
                json.dumps(data, default=str)
            )
            print(f"💾 Cached savings analysis for user {user_id}")
        except Exception as e:
            print(f"❌ Error caching savings analysis: {e}")

    def get_savings_analysis(self, user_id: str) -> Optional[Dict]:
        """Get cached savings analysis"""
        if not self.enabled:
            return None

        try:
            key = f"savings:analysis:{user_id}"
            data = self.redis_client.get(key)
            
            if data:
                cached = json.loads(data)
                print(f"✅ Retrieved cached savings analysis")
                return cached['analysis']
            
            return None
        except Exception as e:
            print(f"❌ Error retrieving savings analysis: {e}")
            return None

    def clear_user_cache(self, user_id: str):
        """Clear all cache for a user"""
        if not self.enabled:
            return

        try:
            patterns = [
                f"chat:{user_id}:*",
                f"conversation:{user_id}",
                f"transactions:current:{user_id}",
                f"savings:analysis:{user_id}"
            ]
            
            for pattern in patterns:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            
            print(f"🗑️ Cleared cache for user {user_id}")
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")


# Global cache instance
redis_cache = RedisCache()
