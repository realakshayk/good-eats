import googlemaps
from app.utils.config import settings

def test_google_maps_api():
    try:
        print(f"API Key length: {len(settings.GOOGLE_MAPS_API_KEY)}")
        print(f"API Key starts with: {settings.GOOGLE_MAPS_API_KEY[:10]}")
        
        client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        
        # Test a simple geocoding request
        result = client.geocode("New York, NY")
        if result:
            print("✅ Google Maps API is working!")
            print(f"Found: {result[0]['formatted_address']}")
        else:
            print("❌ No results found")
            
    except ValueError as e:
        print(f"❌ API Key Error: {e}")
        print("Your API key is invalid. Please check:")
        print("1. The key is correct and complete")
        print("2. The key has the right permissions (Places API, Geocoding API)")
        print("3. Billing is enabled in Google Cloud Console")
    except Exception as e:
        print(f"❌ Other Error: {e}")

if __name__ == "__main__":
    test_google_maps_api() 