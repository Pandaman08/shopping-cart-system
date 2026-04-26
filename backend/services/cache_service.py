import redis
import json
from typing import Optional, Any
import os
import time
from dotenv import load_dotenv

load_dotenv()

class CacheService:
    def __init__(self):
        self._memory_cache: dict[str, tuple[str, float]] = {}
        self._redis_enabled = True
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            self.redis_client.ping()
        except Exception:
            self._redis_enabled = False
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[str]:
        if self._redis_enabled and self.redis_client is not None:
            return self.redis_client.get(key)

        cached = self._memory_cache.get(key)
        if not cached:
            return None

        value, expires_at = cached
        if expires_at < time.time():
            self._memory_cache.pop(key, None)
            return None
        return value
    
    async def set(self, key: str, value: str, expire: int = 300):
        if self._redis_enabled and self.redis_client is not None:
            self.redis_client.setex(key, expire, value)
            return

        self._memory_cache[key] = (value, time.time() + expire)
    
    async def delete(self, key: str):
        if self._redis_enabled and self.redis_client is not None:
            self.redis_client.delete(key)
            return

        self._memory_cache.pop(key, None)
    
    async def clear_pattern(self, pattern: str):
        if self._redis_enabled and self.redis_client is not None:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return

        if pattern == "*":
            self._memory_cache.clear()
            return

        if pattern.endswith("*"):
            prefix = pattern[:-1]
            keys_to_remove = [k for k in self._memory_cache.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                self._memory_cache.pop(key, None)

async def get_cache():
    return CacheService()