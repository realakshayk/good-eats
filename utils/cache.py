import redis
import os
import yaml
import hashlib
import json
import time
from typing import Any, Callable

CACHE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/cache.yaml')
try:
    with open(CACHE_CONFIG_PATH) as f:
        CACHE_TTLS = yaml.safe_load(f).get('cache', {})
except Exception:
    CACHE_TTLS = {}

REDIS_URI = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
try:
    redis_client = redis.Redis.from_url(REDIS_URI)
    redis_client.ping()
except Exception:
    redis_client = None

FILE_CACHE_DIR = os.path.join(os.path.dirname(__file__), '../logs/file_cache')
os.makedirs(FILE_CACHE_DIR, exist_ok=True)

def _file_cache_path(key: str) -> str:
    h = hashlib.sha256(key.encode()).hexdigest()
    return os.path.join(FILE_CACHE_DIR, f'{h}.json')

def get_or_set_cache(key: str, ttl: int, fetch_fn: Callable[[], Any]) -> Any:
    # Try Redis
    if redis_client:
        try:
            val = redis_client.get(key)
            if val:
                return json.loads(val)
        except Exception:
            pass
    # Try file cache
    path = _file_cache_path(key)
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
            if time.time() < data.get('expires', 0):
                return data['value']
    # Fetch and cache
    value = fetch_fn()
    # Set Redis
    if redis_client:
        try:
            redis_client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass
    # Set file cache
    with open(path, 'w') as f:
        json.dump({'value': value, 'expires': time.time() + ttl}, f)
    return value

def invalidate_cache(key: str):
    # Invalidate Redis
    if redis_client:
        try:
            redis_client.delete(key)
        except Exception:
            pass
    # Invalidate file cache
    path = _file_cache_path(key)
    if os.path.exists(path):
        os.remove(path) 