from flask import request, jsonify
from functools import wraps
from typing import Dict
import time

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.blocked_ips: Dict[str, float] = {}

    def _get_client_ip(self) -> str:
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return request.remote_addr

    def check_rate_limit(self, max_requests: int, window_seconds: int) -> tuple[bool, str]:
        ip = self._get_client_ip()

        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return False, "Rate limit exceeded. Please try again later."
            else:
                del self.blocked_ips[ip]

        cutoff = time.time() - window_seconds

        if ip not in self.requests:
            self.requests[ip] = []

        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]

        if len(self.requests[ip]) >= max_requests:
            self.blocked_ips[ip] = time.time() + 900  # Block for 15 minutes
            return False, "Too many requests"

        self.requests[ip].append(time.time())
        return True, "OK"

rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            allowed, message = rate_limiter.check_rate_limit(max_requests, window_seconds)

            if not allowed:
                return jsonify({"error": message}), 429

            return f(*args, **kwargs)

        return decorated
    return decorator
