import redis
import json
from typing import Optional, Any
import os
from dotenv import load_dotenv

load_dotenv()

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[str]:
        return self.redis_client.get(key)
    
    async def set(self, key: str, value: str, expire: int = 300):
        self.redis_client.setex(key, expire, value)
    
    async def delete(self, key: str):
        self.redis_client.delete(key)
    
    async def clear_pattern(self, pattern: str):
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)

async def get_cache():
    return CacheService()