import httpx
import asyncio
import os
import json
from typing import List, Dict, Any, Optional
from config.config import get_settings
import structlog
import redis
from core.errors import MealDiscoveryError

logger = structlog.get_logger()

REDIS_TTL = 3600  # 1 hour default
CACHE_PREFIX = "places:"
MOCK_PLACES_PATH = "services/mock_places.json"

class GooglePlacesClient:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_API_KEY
        self.mock_mode = getattr(self.settings, "MOCK_MODE", False)
        self.redis_uri = self.settings.REDIS_URI
        self.redis = None
        try:
            self.redis = redis.Redis.from_url(self.redis_uri)
            self.redis.ping()
        except Exception:
            logger.warn("redis.unavailable", uri=self.redis_uri)
            self.redis = None

    async def discover_places(self, lat: float, lng: float, radius: float, keyword: str, refresh: bool = False) -> List[Dict[str, Any]]:
        cache_key = f"{CACHE_PREFIX}{lat}:{lng}:{radius}:{keyword}"
        if not refresh:
            cached = await self._get_cache(cache_key)
            if cached:
                return cached
        if self.mock_mode:
            return self._load_mock_places()
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": int(radius * 1000),
            "type": "restaurant",
            "keyword": keyword,
            "key": self.api_key
        }
        async with httpx.AsyncClient(timeout=10) as client:
            for attempt in range(3):
                try:
                    resp = await client.get(url, params=params)
                    data = resp.json()
                    if data.get("status") == "OK":
                        places = [
                            {
                                "name": p["name"],
                                "place_id": p["place_id"],
                                "location": p["geometry"]["location"],
                                "rating": p.get("rating"),
                                "open_now": p.get("opening_hours", {}).get("open_now"),
                                "website": p.get("website")
                            }
                            for p in data.get("results", [])
                        ]
                        await self._set_cache(cache_key, places)
                        return places
                    elif data.get("status") == "OVER_QUERY_LIMIT":
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        logger.error("places.error", status=data.get("status"), error=data)
                        raise MealDiscoveryError(f"Google Places error: {data.get('status')}")
                except Exception as e:
                    logger.error("places.http_error", error=str(e))
                    if attempt == 2:
                        raise MealDiscoveryError("Failed to fetch places after retries.")
                    await asyncio.sleep(2 ** attempt)
        return []

    async def _get_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        if self.redis:
            try:
                val = self.redis.get(key)
                if val:
                    return json.loads(val)
            except Exception:
                pass
        # File fallback
        if os.path.exists(MOCK_PLACES_PATH):
            with open(MOCK_PLACES_PATH, "r") as f:
                return json.load(f)
        return None

    async def _set_cache(self, key: str, value: Any):
        if self.redis:
            try:
                self.redis.setex(key, REDIS_TTL, json.dumps(value))
            except Exception:
                pass

    def _load_mock_places(self):
        if os.path.exists(MOCK_PLACES_PATH):
            with open(MOCK_PLACES_PATH, "r") as f:
                return json.load(f)
        return [] 