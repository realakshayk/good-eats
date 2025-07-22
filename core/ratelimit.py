import redis
import yaml
import os
import time
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from core.auth import API_KEYS

logger = structlog.get_logger()

RATE_LIMITS_PATH = os.path.join(os.path.dirname(__file__), '../config/rate_limits.yaml')
REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379/0")

# Load rate limits from YAML
try:
    with open(RATE_LIMITS_PATH, "r") as f:
        RATE_LIMITS = yaml.safe_load(f).get('rate_limits', {})
except Exception:
    RATE_LIMITS = {
        "free": {"rpm": 10, "rph": 100},
        "premium": {"rpm": 60, "rph": 1000},
        "enterprise": {"rpm": 300, "rph": 10000}
    }

redis_client = redis.Redis.from_url(REDIS_URI)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = getattr(request.state, "api_key", None)
        plan = getattr(request.state, "api_plan", "free")
        limits = RATE_LIMITS.get(plan, {"rpm": 10, "rph": 100})
        now = int(time.time())
        minute = now // 60
        hour = now // 3600
        rpm_key = f"ratelimit:{api_key}:m:{minute}"
        rph_key = f"ratelimit:{api_key}:h:{hour}"
        rpm = redis_client.incr(rpm_key)
        rph = redis_client.incr(rph_key)
        redis_client.expire(rpm_key, 70)
        redis_client.expire(rph_key, 3700)
        remaining_min = max(0, limits["rpm"] - rpm)
        remaining_hour = max(0, limits["rph"] - rph)
        reset_min = 60 - (now % 60)
        reset_hour = 3600 - (now % 3600)
        if rpm > limits["rpm"] or rph > limits["rph"]:
            logger.warn("ratelimit.exceeded", api_key=api_key, plan=plan, rpm=rpm, rph=rph)
            headers = {
                "X-RateLimit-Remaining": str(0),
                "X-RateLimit-Reset": str(min(reset_min, reset_hour)),
                "Retry-After": str(min(reset_min, reset_hour))
            }
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded", headers=headers)
        response: Response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(min(remaining_min, remaining_hour))
        response.headers["X-RateLimit-Reset"] = str(min(reset_min, reset_hour))
        return response 