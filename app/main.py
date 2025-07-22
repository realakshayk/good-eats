from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List

from app.models import (
    RecommendationRequest, 
    RecommendationResponse, 
    HealthCheckResponse,
    RestaurantWithMeals,
    FitnessGoal
)
from app.services.google_places import GooglePlacesService
from app.services.menu_scraper import MenuScraperService
from app.services.llm_analyzer import LLMAnalyzerService
from app.utils.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Good Eats API",
    description="Health-tech product for meal recommendations based on fitness goals",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
google_places_service = GooglePlacesService()
menu_scraper_service = MenuScraperService()
llm_analyzer_service = LLMAnalyzerService()

@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    try:
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse()

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get meal recommendations based on fitness goal and location.
    
    This endpoint:
    1. Searches for restaurants near the specified location
    2. Scrapes menus from restaurant websites
    3. Analyzes menu items using LLM
    4. Filters and ranks recommendations based on fitness goal
    """
    try:
        logger.info(f"Processing recommendation request for {request.fitness_goal} in {request.location}")
        
        # Step 1: Search for restaurants
        restaurants = await google_places_service.search_restaurants(
            location=request.location,
            max_results=settings.MAX_RESTAURANTS
        )
        
        if not restaurants:
            raise HTTPException(
                status_code=404,
                detail=f"No restaurants found near {request.location}"
            )
        
        logger.info(f"Found {len(restaurants)} restaurants")
        
        # Step 2: Scrape menus from restaurants with websites
        restaurants_with_websites = [r for r in restaurants if r.website]
        if not restaurants_with_websites:
            raise HTTPException(
                status_code=404,
                detail="No restaurants with accessible websites found"
            )
        
        menu_data = await menu_scraper_service.scrape_multiple_menus(restaurants_with_websites)
        
        # Step 3: Analyze menu items and create recommendations
        recommendations = []
        total_meals_analyzed = 0
        
        for restaurant in restaurants_with_websites:
            menu_items = menu_data.get(restaurant.place_id, [])
            if not menu_items:
                continue
            
            # Analyze menu items
            analyzed_items = await llm_analyzer_service.analyze_menu_items(
                menu_items, 
                request.fitness_goal
            )
            
            # Filter by goal
            filtered_items = await llm_analyzer_service.filter_by_goal(
                analyzed_items, 
                request.fitness_goal
            )
            
            if filtered_items:
                restaurant_with_meals = RestaurantWithMeals(
                    restaurant=restaurant,
                    meals=filtered_items[:request.max_recommendations]
                )
                recommendations.append(restaurant_with_meals)
                total_meals_analyzed += len(analyzed_items)
        
        # Sort recommendations by number of relevant meals
        recommendations.sort(key=lambda x: len(x.meals), reverse=True)
        
        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"No suitable meals found for {request.fitness_goal} goal"
            )
        
        # Limit to requested number of recommendations
        recommendations = recommendations[:request.max_recommendations]
        
        logger.info(f"Generated {len(recommendations)} recommendations with {total_meals_analyzed} meals analyzed")
        
        return RecommendationResponse(
            recommendations=recommendations,
            total_restaurants_found=len(restaurants),
            total_meals_analyzed=total_meals_analyzed,
            search_location=request.location,
            fitness_goal=request.fitness_goal
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing recommendation request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing recommendation request"
        )

@app.get("/goals")
async def get_supported_goals():
    """Get list of supported fitness goals."""
    return {
        "goals": [
            {"value": goal.value, "description": goal.name.replace("_", " ").title()}
            for goal in FitnessGoal
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 