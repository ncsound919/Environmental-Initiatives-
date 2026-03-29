"""
ECOS API Rate Limiting Middleware
Redis-backed sliding window rate limiter with per-plan limits.
Applies to all FastAPI routes in the api-gateway.
"""
from __future__ import annotations

import time
import os
from typing import Callable, Awaitable

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Per-plan rate limits (requests per minute)
# ---------------------------------------------------------------------------
PLAN_LIMITS: dict[str, int] = {
    "free": 60,          # 60 req/min
    "pro": 1_000,        # 1,000 req/min
    "enterprise": 10_000, # 10,000 req/min
    "device": 500,       # IoT device MQTT bridge
    "internal": 99_999,  # Internal service calls (CI, seed scripts)
}

# Routes that are exempt from rate limiting
EXEMPT_PATHS: set[str] = {
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/webhooks/stripe",  # Stripe webhooks must not be rate-limited
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window rate limiter backed by Redis.
    Falls back to an in-memory counter if Redis is unavailable (dev mode).
    """

    def __init__(self, app: ASGIApp, redis_url: str | None = None) -> None:
        super().__init__(app)
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self._redis: "aioredis.Redis | None" = None
        self._memory_store: dict[str, list[float]] = {}  # fallback

    async def _get_redis(self) -> "aioredis.Redis | None":
        if not REDIS_AVAILABLE:
            return None
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(
                    self._redis_url, encoding="utf-8", decode_responses=True
                )
                await self._redis.ping()
            except Exception:
                self._redis = None
        return self._redis

    def _get_plan_from_request(self, request: Request) -> str:
        """Extract ECOS plan from JWT claims in request state (set by auth middleware)."""
        plan = getattr(request.state, "ecos_plan", "free")
        return plan if plan in PLAN_LIMITS else "free"

    def _get_client_key(self, request: Request) -> str:
        """Build a unique key: auth user ID or IP address."""
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"rl:user:{user_id}"
        # Fallback to client IP (support X-Forwarded-For from load balancer)
        forwarded = request.headers.get("x-forwarded-for")
        ip = forwarded.split(",")[0].strip() if forwarded else request.client.host  # type: ignore
        return f"rl:ip:{ip}"

    async def _check_rate_limit_redis(
        self, redis: "aioredis.Redis", key: str, limit: int, window: int = 60
    ) -> tuple[bool, int, int]:
        """
        Sliding window using a Redis sorted set.
        Returns (allowed, current_count, reset_at_unix).
        """
        now = time.time()
        window_start = now - window
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, "-inf", window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window)
        results = await pipe.execute()
        count: int = results[2]
        reset_at = int(now) + window
        return count <= limit, count, reset_at

    def _check_rate_limit_memory(
        self, key: str, limit: int, window: int = 60
    ) -> tuple[bool, int, int]:
        """In-memory fallback (not suitable for multi-process production)."""
        now = time.time()
        window_start = now - window
        timestamps = self._memory_store.get(key, [])
        timestamps = [t for t in timestamps if t > window_start]
        timestamps.append(now)
        self._memory_store[key] = timestamps
        count = len(timestamps)
        reset_at = int(now) + window
        return count <= limit, count, reset_at

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip exempt paths
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        plan = self._get_plan_from_request(request)
        limit = PLAN_LIMITS[plan]
        key = self._get_client_key(request)

        redis = await self._get_redis()
        if redis:
            allowed, count, reset_at = await self._check_rate_limit_redis(
                redis, key, limit
            )
        else:
            allowed, count, reset_at = self._check_rate_limit_memory(key, limit)

        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, limit - count)),
            "X-RateLimit-Reset": str(reset_at),
            "X-RateLimit-Plan": plan,
        }

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "plan": plan,
                    "limit": limit,
                    "window_seconds": 60,
                    "retry_after": reset_at - int(time.time()),
                    "upgrade_url": "https://ecos.app/pricing",
                },
                headers=headers,
            )

        response = await call_next(request)
        for header, value in headers.items():
            response.headers[header] = value
        return response


def add_rate_limiting(app: "FastAPI", redis_url: str | None = None) -> None:  # type: ignore[name-defined]
    """Convenience function to mount rate limiting on a FastAPI app."""
    app.add_middleware(RateLimitMiddleware, redis_url=redis_url)
