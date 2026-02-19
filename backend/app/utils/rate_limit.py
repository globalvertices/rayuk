"""Basic in-memory rate limiter for MVP."""

import time
from collections import defaultdict

from fastapi import Request

from app.core.exceptions import BadRequestError

# In-memory storage: {key: [timestamp, ...]}
_requests: dict[str, list[float]] = defaultdict(list)


def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """Rate limit decorator for FastAPI endpoints.

    Args:
        max_requests: Maximum number of requests allowed in the window.
        window_seconds: Time window in seconds.
    """
    async def _check(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"
        now = time.time()

        # Clean old entries
        _requests[key] = [t for t in _requests[key] if t > now - window_seconds]

        if len(_requests[key]) >= max_requests:
            raise BadRequestError("Too many requests. Please try again later.")

        _requests[key].append(now)

    return _check
