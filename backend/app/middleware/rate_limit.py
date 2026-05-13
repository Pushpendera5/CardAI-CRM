"""
Sliding-window rate limiter middleware.

Uses Redis (sorted sets) when available for accurate multi-worker rate limiting.
Falls back to a per-process in-memory deque when Redis is unreachable.
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import get_settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP-based rate limiter: max `rate_limit_per_minute` requests per 60-second window."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self._redis = None
        self._redis_ok: bool | None = None  # None = not yet tried
        # Fallback in-memory store (per-process only)
        self._memory: dict[str, deque[float]] = defaultdict(deque)

    # ── Redis helpers ─────────────────────────────────────────────────────────

    def _get_redis(self):
        """Return a live Redis client or None if unavailable."""
        if self._redis_ok is False:
            return None  # Already determined unavailable — skip retry overhead
        try:
            import redis  # imported lazily so Redis is truly optional

            client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            client.ping()
            self._redis = client
            self._redis_ok = True
            return client
        except Exception as exc:
            if self._redis_ok is not False:
                logger.warning("Rate limiter: Redis unavailable (%s). Falling back to in-memory.", exc)
            self._redis_ok = False
            return None

    def _check_redis(self, client, client_ip: str) -> bool:
        """Sliding-window check via Redis sorted set.  Returns True if limit NOT exceeded."""
        key = f"rl:{client_ip}"
        now = time.time()
        window_start = now - 60.0
        try:
            pipe = client.pipeline(transaction=False)
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {f"{now}:{id(pipe)}": now})  # unique member per request
            pipe.expire(key, 60)
            results = pipe.execute()
            count: int = results[1]
            return count < settings.rate_limit_per_minute
        except Exception as exc:
            logger.warning("Rate limiter Redis error: %s — falling back to in-memory.", exc)
            self._redis_ok = False
            return True  # fail-open on Redis error

    def _check_memory(self, client_ip: str) -> bool:
        """In-memory sliding-window check.  NOT safe for multi-process deployments."""
        bucket = self._memory[client_ip]
        window_start = time.time() - 60.0
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_per_minute:
            return False
        bucket.append(time.time())
        return True

    # ── Middleware dispatch ───────────────────────────────────────────────────

    async def dispatch(self, request: Request, call_next):
        if settings.app_env == "test":
            return await call_next(request)

        client_ip: str = (request.client.host if request.client else None) or "unknown"

        r = self._get_redis()
        if r:
            allowed = self._check_redis(r, client_ip)
        else:
            allowed = self._check_memory(client_ip)

        if not allowed:
            raise AppError("Rate limit exceeded. Please slow down.", 429)

        return await call_next(request)

