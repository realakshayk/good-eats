import os
import redis
REDIS_URI = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
try:
    r = redis.Redis.from_url(REDIS_URI)
    r.flushdb()
    print('Redis cache cleared.')
except Exception as e:
    print('Redis unavailable, skipping.')
    # Optionally clear file fallback here 