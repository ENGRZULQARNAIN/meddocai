"""
A minimal example of a rate-limited route, kept here purely as a
reference for wiring `Depends(rate_limit(...))` onto real endpoints as
they're built. The limit itself (5 requests / 10 seconds per client IP)
is arbitrary — tune it per endpoint once there's a real one to protect.
"""
from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit

router = APIRouter()


@router.get("/ping", dependencies=[Depends(rate_limit(times=5, seconds=10, scope="ping"))])
async def ping() -> dict:
    return {"pong": True}
