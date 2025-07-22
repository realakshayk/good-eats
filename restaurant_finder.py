import requests
import os
import logging
from typing import List, Dict, Optional
from urllib.parse import quote
import requests_cache
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure requests cache for 24 hours
requests_cache.install_cache(
    '.gcache',
    expire_after=timedelta(hours=24),
    allowable_methods=('GET', 'POST'),
    allowable_codes=(200, 201, 202, 203, 204, 205, 206, 207, 208, 226)
)

def get_nearby_restaurants(location: str, keyword: str = "healthy food") -> List[Dict]:
    """
    Find nearby restaurants using Google Places API.
    
    Args:
        location: Location string (e.g., "Brooklyn, NY")
        keyword: Search keyword for restaurants (default: "healthy food")
        
    Returns:
        List of dictionaries containing restaurant information with:
        - name: Restaurant name
        - website: Restaurant website URL
        - place_id: Google Places ID
    """
    
    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    restaurants = []
    
    try:
        # Step 1: Geocode the location to get coordinates
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            'address': location,
            'key': api_key
        }
        
        logger.info(f"Geocoding location: {location}")
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()
        
        if geocode_data['status'] != 'OK':
            logger.error(f"Geocoding failed: {geocode_data['status']}")
            return []
        
        # Extract coordinates
        location_data = geocode_data['results'][0]['geometry']['location']
        lat = location_data['lat']
        lng = location_data['lng']
        
        logger.info(f"Found coordinates: {lat}, {lng}")
        
        # Step 2: Search for nearby restaurants
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places_params = {
            'location': f"{lat},{lng}",
            'radius': 5000,  # 5km radius
            'type': 'restaurant',
            'keyword': keyword,
            'key': api_key
        }
        
        logger.info(f"Searching for restaurants with keyword: {keyword}")
        places_response = requests.get(places_url, params=places_params)
        places_response.raise_for_status()
        places_data = places_response.json()
        
        if places_data['status'] != 'OK' and places_data['status'] != 'ZERO_RESULTS':
            logger.error(f"Places search failed: {places_data['status']}")
            return []
        
        if places_data['status'] == 'ZERO_RESULTS':
            logger.info("No restaurants found")
            return []
        
        # Step 3: Get detailed information for each restaurant
        for place in places_data.get('results', []):
            place_id = place['place_id']
            
            # Get detailed place information
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                'place_id': place_id,
                'fields': 'name,website,place_id',
                'key': api_key
            }
            
            details_response = requests.get(details_url, params=details_params)
            details_response.raise_for_status()
            details_data = details_response.json()
            
            if details_data['status'] == 'OK':
                place_details = details_data['result']
                
                # Only include restaurants with websites
                if 'website' in place_details and place_details['website']:
                    restaurant = {
                        'name': place_details.get('name', 'Unknown'),
                        'website': place_details['website'],
                        'place_id': place_details.get('place_id', place_id)
                    }
                    restaurants.append(restaurant)
                    logger.info(f"Found restaurant: {restaurant['name']}")
                else:
                    logger.debug(f"Skipping {place_details.get('name', 'Unknown')} - no website")
        
        # Limit to 5 restaurants
        restaurants = restaurants[:5]
        
        logger.info(f"Found {len(restaurants)} restaurants with websites")
        return restaurants
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Google Places API request error: {str(e)}")
        raise Exception(f"Google Places API request failed: {str(e)}")
    except requests.exceptions.Timeout as e:
        logger.error(f"Google Places API timeout: {str(e)}")
        raise Exception(f"Google Places API timeout: {str(e)}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Google Places API connection error: {str(e)}")
        raise Exception(f"Google Places API connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in restaurant search: {str(e)}")
        raise Exception(f"Restaurant search failed: {str(e)}")

def test_restaurant_finder():
    """Test function to demonstrate usage."""
    # Set a test API key (you'll need to replace this with a real one)
    os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'
    
    try:
        restaurants = get_nearby_restaurants("Brooklyn, NY", "healthy food")
        
        if restaurants:
            print(f"Found {len(restaurants)} restaurants:")
            for i, restaurant in enumerate(restaurants, 1):
                print(f"{i}. {restaurant['name']}")
                print(f"   Website: {restaurant['website']}")
                print(f"   Place ID: {restaurant['place_id']}")
                print()
        else:
            print("No restaurants found")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_restaurant_finder() 