"""
A small Redis-backed rate limiter dependency.

This is deliberately hand-written rather than via the `fastapi-limiter`
package: that library inspects `request.app.routes` to build its cache
key and assumes every entry has a `.path` attribute, which breaks on
current FastAPI/Starlette once you use `include_router` (it adds
router-wrapper entries without one). Rather than depend on a third-party
internal that's out of sync with the framework, this does the same
atomic check directly against Redis — and it's genuinely small.

The core trick is the Lua script: INCR + (on the first hit) PEXPIRE, in
one round trip. That atomicity is the whole point — it's what makes this
safe under concurrent requests from the same client, and correct across
however many `api` replicas are running, since they all check the same
Redis key instead of each keeping its own in-memory counter.
"""
from math import ceil
from typing import Callable

from fastapi import HTTPException, Request
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.redis import redis_client

_LUA_FIXED_WINDOW = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("PEXPIRE", KEYS[1], ARGV[1])
end
return current
"""


def rate_limit(times: int, seconds: int, scope: str) -> Callable:
    """
    FastAPI dependency factory: allow `times` requests per `seconds`,
    per client IP, tracked separately per `scope` so different endpoints
    don't share a counter.

    Usage: Depends(rate_limit(times=5, seconds=10, scope="ping"))
    """
    window_ms = seconds * 1000

    async def _dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{scope}:{client_ip}"

        current = await redis_client.eval(_LUA_FIXED_WINDOW, 1, key, window_ms)
        if int(current) > times:
            ttl_ms = await redis_client.pttl(key)
            raise HTTPException(
                HTTP_429_TOO_MANY_REQUESTS,
                "Too Many Requests",
                headers={"Retry-After": str(ceil(max(ttl_ms, 0) / 1000))},
            )

    return _dependency
