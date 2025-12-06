
import os
import redis
import json
import hashlib
from typing import Optional, Dict, Any, List

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
USE_REDIS_CACHE = os.getenv("USE_REDIS_CACHE", "false").lower() == "true"

class CacheService:
    def __init__(self):
        self.enabled = USE_REDIS_CACHE
        self.client = None
        if self.enabled:
            try:
                self.client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=1
                )
                self.client.ping()
            except Exception as e:
                print(f"Redis Cache Init Warning: {e}")
                self.client = None

    def _get_key(self, org_id: str, query: str) -> str:
        """Generate a consistent cache key."""
        # Using MD5 of query to keep key short and safe
        query_hash = hashlib.md5(query.strip().lower().encode()).hexdigest()
        return f"rag:response:{org_id}:{query_hash}"

    def get_cached_response(self, org_id: str, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if exists."""
        if not self.enabled or not self.client:
            return None
        
        try:
            key = self._get_key(org_id, query)
            data = self.client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            # Fallback to no cache on error
            print(f"Cache GET Error: {e}")
        return None

    def set_cached_response(self, org_id: str, query: str, response: Dict[str, Any], ttl_seconds: int = 86400):
        """Cache a response."""
        if not self.enabled or not self.client:
            return

        try:
            key = self._get_key(org_id, query)
            self.client.setex(
                key,
                ttl_seconds,
                json.dumps(response)
            )
        except Exception as e:
            print(f"Cache SET Error: {e}")

# Global Instance
cache_service = CacheService()
