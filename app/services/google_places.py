import googlemaps
from typing import List, Optional
from app.models import Restaurant
from app.utils.config import settings
import logging

logger = logging.getLogger(__name__)

class GooglePlacesService:
    """Service for interacting with Google Places API."""
    
    def __init__(self):
        self.client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    
    async def search_restaurants(self, location: str, max_results: int = 10) -> List[Restaurant]:
        """
        Search for restaurants near the specified location.
        
        Args:
            location: Location string (e.g., "Brooklyn, NY")
            max_results: Maximum number of restaurants to return
            
        Returns:
            List of Restaurant objects
        """
        try:
            # First, geocode the location to get coordinates
            geocode_result = self.client.geocode(location)
            if not geocode_result:
                logger.error(f"Could not geocode location: {location}")
                return []
            
            lat = geocode_result[0]['geometry']['location']['lat']
            lng = geocode_result[0]['geometry']['location']['lng']
            
            # Search for restaurants
            places_result = self.client.places_nearby(
                location=(lat, lng),
                radius=settings.SEARCH_RADIUS_METERS,
                type='restaurant',
                max_results=max_results
            )
            
            restaurants = []
            for place in places_result.get('results', []):
                # Get detailed information for each place
                place_details = self.client.place(
                    place['place_id'],
                    fields=['place_id', 'name', 'formatted_address', 'rating', 
                           'price_level', 'website', 'formatted_phone_number']
                )
                
                details = place_details.get('result', {})
                restaurant = Restaurant(
                    place_id=details.get('place_id', place['place_id']),
                    name=details.get('name', place.get('name', 'Unknown')),
                    address=details.get('formatted_address', place.get('vicinity', 'Unknown')),
                    rating=details.get('rating'),
                    price_level=details.get('price_level'),
                    website=details.get('website'),
                    phone=details.get('formatted_phone_number')
                )
                restaurants.append(restaurant)
            
            logger.info(f"Found {len(restaurants)} restaurants near {location}")
            return restaurants
            
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            return []
    
    async def get_restaurant_details(self, place_id: str) -> Optional[Restaurant]:
        """
        Get detailed information about a specific restaurant.
        
        Args:
            place_id: Google Places ID
            
        Returns:
            Restaurant object or None if not found
        """
        try:
            place_details = self.client.place(
                place_id,
                fields=['place_id', 'name', 'formatted_address', 'rating', 
                       'price_level', 'website', 'formatted_phone_number']
            )
            
            details = place_details.get('result', {})
            return Restaurant(
                place_id=details.get('place_id'),
                name=details.get('name', 'Unknown'),
                address=details.get('formatted_address', 'Unknown'),
                rating=details.get('rating'),
                price_level=details.get('price_level'),
                website=details.get('website'),
                phone=details.get('formatted_phone_number')
            )
            
        except Exception as e:
            logger.error(f"Error getting restaurant details: {str(e)}")
            return None 