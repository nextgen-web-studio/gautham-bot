# Simple in-memory rate limiting for V1
from cachetools import TTLCache
import time

# Allow 10 requests per minute per user
cache = TTLCache(maxsize=10000, ttl=60)

async def check_rate_limit(user_id: int) -> bool:
    current = cache.get(user_id, 0)
    if current >= 10:
        return False
    cache[user_id] = current + 1
    return True
