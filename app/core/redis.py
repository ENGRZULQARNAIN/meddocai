"""
Redis, scoped deliberately to two jobs: cache + rate limiting. It is not
a task queue — Temporal owns all background/durable execution (see
app/workflows/). Keeping this file's surface small is intentional: it's
the one place that owns the Redis connection lifecycle.
"""
from redis import asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()

# A single shared connection pool for the process — reused by both the
# cache helpers below and FastAPILimiter (wired in app/main.py).
redis_client = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency: yields the shared Redis client."""
    return redis_client
