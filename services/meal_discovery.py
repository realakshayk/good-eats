import asyncio
from typing import List, Dict, Any, Optional
from config.config import get_settings
from services.google_places import GooglePlacesClient
from core.errors import MealDiscoveryError
import structlog

logger = structlog.get_logger()

MOCK_MEALS_PATH = "services/mock_meals.json"

class MealDiscoveryService:
    def __init__(self):
        self.settings = get_settings()
        self.places_client = GooglePlacesClient()
        self.mock_mode = getattr(self.settings, "MOCK_MODE", False)

    async def discover_meals(self, lat: float, lng: float, radius: float, goal: str, macros: Optional[Dict[str, float]] = None, exclusions: Optional[List[str]] = None, flavor_prefs: Optional[List[str]] = None, page: int = 1, page_size: int = 10, refresh: bool = False) -> Dict[str, Any]:
        try:
            if self.mock_mode:
                return self._load_mock_meals()
            # 1. Discover places
            keyword = goal.replace("_", " ")
            places = await self.places_client.discover_places(lat, lng, radius, keyword, refresh=refresh)
            if not places:
                raise MealDiscoveryError("No restaurants found.")
            # 2. Scrape menus (async)
            menu_results = await asyncio.gather(*[
                self._scrape_and_parse_menu(place) for place in places
            ])
            # 3. Score meals
            all_meals = []
            for meals in menu_results:
                if meals:
                    all_meals.extend(meals)
            # 4. Filter, paginate, sort
            all_meals = self._score_and_sort_meals(all_meals, goal, macros, exclusions, flavor_prefs)
            start = (page - 1) * page_size
            end = start + page_size
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
        # Placeholder: In real code, call menu scraper, AI parser, nutrition estimator
        # Fallback to mock meals if needed
        try:
            # Simulate async scraping/parsing
            await asyncio.sleep(0.1)
            return self._load_mock_meals(place=place)
        except Exception:
            logger.warn("menu_scrape.fallback", place=place.get("name"))
            return self._load_mock_meals(place=place)

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