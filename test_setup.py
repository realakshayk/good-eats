#!/usr/bin/env python3
"""
Test script to verify Good Eats MVP setup.
"""

import asyncio
import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        import playwright
        print("✓ Playwright imported successfully")
    except ImportError as e:
        print(f"✗ Playwright import failed: {e}")
        return False
    
    try:
        import openai
        print("✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ OpenAI import failed: {e}")
        return False
    
    try:
        import googlemaps
        print("✓ Google Maps imported successfully")
    except ImportError as e:
        print(f"✗ Google Maps import failed: {e}")
        return False
    
    try:
        from app.models import FitnessGoal, MealTag
        print("✓ App models imported successfully")
    except ImportError as e:
        print(f"✗ App models import failed: {e}")
        return False
    
    try:
        from app.utils.config import settings
        print("✓ App config imported successfully")
    except ImportError as e:
        print(f"✗ App config import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration validation."""
    print("\nTesting configuration...")
    
    try:
        from app.utils.config import settings
        
        # Test if API keys are set (they might be empty in test)
        print(f"✓ Google Maps API Key: {'Set' if settings.GOOGLE_MAPS_API_KEY else 'Not set'}")
        print(f"✓ OpenAI API Key: {'Set' if settings.OPENAI_API_KEY else 'Not set'}")
        print(f"✓ Max Restaurants: {settings.MAX_RESTAURANTS}")
        print(f"✓ Max Recommendations: {settings.MAX_RECOMMENDATIONS}")
        print(f"✓ Search Radius: {settings.SEARCH_RADIUS_METERS}m")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

async def test_services():
    """Test service initialization."""
    print("\nTesting services...")
    
    try:
        from app.services.google_places import GooglePlacesService
        from app.services.menu_scraper import MenuScraperService
        from app.services.llm_analyzer import LLMAnalyzerService
        
        # Initialize services
        google_service = GooglePlacesService()
        scraper_service = MenuScraperService()
        llm_service = LLMAnalyzerService()
        
        print("✓ All services initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Good Eats MVP Setup Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Test configuration
    if not test_config():
        print("\n❌ Configuration test failed.")
        sys.exit(1)
    
    # Test services
    if not asyncio.run(test_services()):
        print("\n❌ Service tests failed.")
        sys.exit(1)
    
    print("\n✅ All tests passed! Setup is complete.")
    print("\nNext steps:")
    print("1. Copy env_template.txt to .env")
    print("2. Add your API keys to .env")
    print("3. Run: uvicorn app.main:app --reload")
    print("4. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 