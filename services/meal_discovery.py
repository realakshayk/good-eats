import asyncio
from typing import List, Dict, Any, Optional
from config.config import get_settings
from services.google_places import GooglePlacesClient
from core.errors import MealDiscoveryError
import structlog
from utils.logger import add_request_latency
import time
import os
from parsers.openai_parser import OpenAIParser
from parsers.fallback_parser import FallbackParser
from core.analytics import log_event
import httpx

logger = structlog.get_logger()

MOCK_MEALS_PATH = "services/mock_meals.json"

UBER_EATS_API_KEY = os.getenv('UBER_EATS_API_KEY', '')
UBER_EATS_ENDPOINT = 'https://api.ubereatsscraper.com/v1/meals/nearby'
RESTAURANTS_API_ENDPOINT = 'https://api.restaurants.com/v1/meals/nearby'  # Placeholder

class MealDiscoveryService:
    def __init__(self):
        self.settings = get_settings()
        self.places_client = GooglePlacesClient()
        self.mock_mode = getattr(self.settings, "MOCK_MODE", False)
        self.playwright_semaphore = asyncio.Semaphore(3)  # Cap Playwright concurrency
        self.openai_parser = OpenAIParser()
        # Remove Documenu and fallback parser init

    async def discover_meals(self, lat: float, lng: float, radius: float, goal: str, macros: Optional[Dict[str, float]] = None, exclusions: Optional[List[str]] = None, flavor_prefs: Optional[List[str]] = None, page: int = 1, page_size: int = 10, refresh: bool = False) -> Dict[str, Any]:
        t0 = time.time()
        try:
            if self.mock_mode:
                return self._load_mock_meals()
            # 1. Discover places
            t_places = time.time()
            keyword = goal.replace("_", " ")
            places = await self.places_client.discover_places(lat, lng, radius, keyword, refresh=refresh)
            t_places_done = time.time()
            if not places:
                raise MealDiscoveryError("No restaurants found.")
            # 2. Scrape menus (async, capped concurrency)
            async def scrape_with_semaphore(place):
                async with self.playwright_semaphore:
                    return await self._scrape_and_parse_menu(place)
            t_scrape = time.time()
            menu_results = await asyncio.gather(*[
                scrape_with_semaphore(place) for place in places
            ])
            t_scrape_done = time.time()
            # 3. Score meals
            t_score = time.time()
            all_meals = []
            for meals in menu_results:
                if meals:
                    all_meals.extend(meals)
            all_meals = self._score_and_sort_meals(all_meals, goal, macros, exclusions, flavor_prefs)
            t_score_done = time.time()
            # 4. Filter, paginate, sort
            start = (page - 1) * page_size
            end = start + page_size
            # Log step durations
            logger.info("meal_discovery.latency", total=time.time()-t0, places=t_places_done-t_places, scrape=t_scrape_done-t_scrape, score=t_score_done-t_score)
            add_request_latency("meal_discovery", (time.time()-t0)*1000)
            return {
                "meals": all_meals[start:end],
                "total": len(all_meals),
                "page": page,
                "page_size": page_size
            }
        except MealDiscoveryError as e:
            logger.error("meal_discovery.error", error=e.message)
            raise
        except Exception as e:
            logger.error("meal_discovery.unknown_error", error=str(e))
            raise MealDiscoveryError("Unknown error in meal discovery.")

    async def _scrape_and_parse_menu(self, place: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            # 1. Uber Eats Scraper API
            meals = await self._fetch_ubereats_meals(place)
            if meals:
                return meals
            log_event('fallback_used', {'method': 'restaurants_api', 'place': place.get('name')})
            # 2. Restaurants API fallback
            meals = await self._fetch_restaurants_api_meals(place)
            if meals:
                return meals
            log_event('fallback_used', {'method': 'static_mock', 'place': place.get('name')})
            # 3. Static mock data fallback
            return self._load_static_mock(place)
        except Exception as e:
            log_event('fallback_used', {'method': 'static_mock', 'place': place.get('name'), 'error': str(e)})
            return self._load_static_mock(place)

    async def _fetch_ubereats_meals(self, place: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not UBER_EATS_API_KEY:
            return []
        params = {
            'lat': place.get('location', {}).get('lat'),
            'lon': place.get('location', {}).get('lon'),
            'radius': 3000,  # meters, example
        }
        headers = {'Authorization': f'Bearer {UBER_EATS_API_KEY}'}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(UBER_EATS_ENDPOINT, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    # Parse Uber Eats response to meal list (simplified)
                    meals = []
                    for m in data.get('meals', []):
                        meals.append({
                            'name': m.get('name'),
                            'description': m.get('description'),
                            'price': m.get('price'),
                            'tags': m.get('tags', []),
                            'relevance_score': m.get('score', 0.5),
                            'confidence_level': 'high',
                            'estimation_origin': 'api',
                            'restaurant': m.get('restaurant', {}),
                            'nutrition': m.get('nutrition', {}),
                        })
                    return meals
        except Exception:
            pass
        return []

    async def _fetch_restaurants_api_meals(self, place: Dict[str, Any]) -> List[Dict[str, Any]]:
        params = {
            'lat': place.get('location', {}).get('lat'),
            'lon': place.get('location', {}).get('lon'),
            'radius': 3000,
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(RESTAURANTS_API_ENDPOINT, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    meals = []
                    for m in data.get('meals', []):
                        meals.append({
                            'name': m.get('name'),
                            'description': m.get('description'),
                            'price': m.get('price'),
                            'tags': m.get('tags', []),
                            'relevance_score': m.get('score', 0.5),
                            'confidence_level': 'medium',
                            'estimation_origin': 'api',
                            'restaurant': m.get('restaurant', {}),
                            'nutrition': m.get('nutrition', {}),
                        })
                    return meals
        except Exception:
            pass
        return []

    def _load_static_mock(self, place: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        import os, json
        goal = (place.get('goal') if place else None) or 'balanced'
        static_path = os.path.join(os.path.dirname(__file__), f'../static/mock_data/{goal}.json')
        if os.path.exists(static_path):
            with open(static_path) as f:
                return json.load(f)
        return [{
            "id": "mock1",
            "name": "Grilled Chicken Bowl",
            "restaurant": place["name"] if place else "Mock Restaurant",
            "nutrition": {"calories": 500, "protein": 40, "carbs": 45, "fat": 15},
            "score": 80
        }]

    def _score_and_sort_meals(self, meals: List[Dict[str, Any]], goal: str, macros, exclusions, flavor_prefs) -> List[Dict[str, Any]]:
        # Placeholder: In real code, call scoring engine
        # For now, just return meals sorted by mock score
        return sorted(meals, key=lambda m: m.get("score", 0), reverse=True)

    def _load_mock_meals(self, place: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        import os, json
        if os.path.exists(MOCK_MEALS_PATH):
            with open(MOCK_MEALS_PATH, "r") as f:
                meals = json.load(f)
                if place:
                    # Filter by place if needed
                    return [m for m in meals if m.get("restaurant") == place.get("name")]
                return meals
        # Return a default mock meal if file missing
        return [{
            "id": "mock1",
            "name": "Grilled Chicken Bowl",
            "restaurant": place["name"] if place else "Mock Restaurant",
            "nutrition": {"calories": 500, "protein": 40, "carbs": 45, "fat": 15},
            "score": 80
        }] 