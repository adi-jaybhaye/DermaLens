import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status


class SimpleRateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.history: Dict[str, List[float]] = defaultdict(list)

    def check(self, request: Request, identifier: str = None) -> bool:
        """Check if request from client IP is within limit."""
        client_ip = identifier or (request.client.host if request.client else "unknown")
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old timestamps
        self.history[client_ip] = [
            ts for ts in self.history[client_ip] if ts > window_start
        ]

        if len(self.history[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        self.history[client_ip].append(now)
        return True


# Preconfigured rate limiters
auth_limiter = SimpleRateLimiter(max_requests=10, window_seconds=60)      # 10 req/min for auth
upload_limiter = SimpleRateLimiter(max_requests=20, window_seconds=60)    # 20 uploads/min
api_limiter = SimpleRateLimiter(max_requests=100, window_seconds=60)     # 100 req/min general
