from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import os

# Import our custom functions
from restaurant_finder import get_nearby_restaurants
from menu_scraper import scrape_menu_text
from meal_extractor import extract_meals_from_menu
from meal_ranker import rank_meals

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Good Eats API",
    description="Health-tech product for meal recommendations based on fitness goals",
    version="1.0.0"
)

class RecommendationRequest(BaseModel):
    goal: str
    location: str

class MealSuggestion(BaseModel):
    meal_name: str
    description: str
    tags: List[str]
    restaurant_name: str
    restaurant_website: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Good Eats API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/recommend", response_model=List[MealSuggestion])
async def get_recommendations(request: RecommendationRequest):
    """
    Get meal recommendations based on fitness goal and location.
    
    This implementation:
    1. Finds nearby restaurants using Google Places API
    2. Scrapes menu text from restaurant websites
    3. Extracts and analyzes meals using OpenAI
    4. Ranks meals by relevance and returns top 5
    """
    
    try:
        logger.info(f"Starting recommendation process for goal: '{request.goal}' in location: '{request.location}'")
        
        # Step 1: Parse the goal and location from the input
        goal = request.goal
        location = request.location
        logger.info(f"Parsed goal: '{goal}', location: '{location}'")
        
        # Step 2: Call get_nearby_restaurants(location) with error handling
        logger.info(f"Searching for restaurants near '{location}'")
        try:
            restaurants = get_nearby_restaurants(location)
            logger.info(f"Found {len(restaurants)} restaurants with websites")
        except Exception as e:
            logger.error(f"Google Places API failed: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Restaurant search service is temporarily unavailable. Please try again later."
            )
        
        if not restaurants:
            raise HTTPException(
                status_code=404,
                detail=f"No restaurants with accessible websites found near {location}"
            )
        
        # Step 3: For each restaurant, get its website and run scrape_menu_text(website)
        all_meals = []
        successful_restaurants = 0
        failed_restaurants = 0
        
        for i, restaurant in enumerate(restaurants, 1):
            restaurant_name = restaurant['name']
            website = restaurant['website']
            
            logger.info(f"Processing restaurant {i}/{len(restaurants)}: {restaurant_name}")
            logger.info(f"Scraping menu from: {website}")
            
            try:
                # Scrape menu text from restaurant website
                menu_text = scrape_menu_text(website)
                
                if not menu_text or len(menu_text.strip()) < 50:
                    logger.warning(f"Insufficient menu text from {restaurant_name}, skipping")
                    failed_restaurants += 1
                    continue
                
                logger.info(f"Successfully scraped {len(menu_text)} characters from {restaurant_name}")
                
                # Step 4: Send menu text and goal to extract_meals_from_menu
                logger.info(f"Extracting meals from {restaurant_name} for goal: '{goal}'")
                try:
                    meals = extract_meals_from_menu(menu_text, goal)
                    
                    # Add restaurant information to each meal
                    for meal in meals:
                        meal['restaurant_name'] = restaurant_name
                        meal['restaurant_website'] = website
                    
                    logger.info(f"Extracted {len(meals)} meals from {restaurant_name}")
                    all_meals.extend(meals)
                    successful_restaurants += 1
                    
                except Exception as e:
                    logger.error(f"OpenAI meal extraction failed for {restaurant_name}: {str(e)}")
                    failed_restaurants += 1
                    continue
                
            except Exception as e:
                logger.error(f"Error processing {restaurant_name} (website/Playwright issue): {str(e)}")
                failed_restaurants += 1
                continue
        
        # Step 5: Aggregate all returned meals
        logger.info(f"Total meals collected: {len(all_meals)} from {successful_restaurants} restaurants")
        logger.info(f"Failed to process {failed_restaurants} restaurants")
        
        if not all_meals:
            raise HTTPException(
                status_code=404,
                detail=f"No suitable meals found for goal '{goal}' in {location}. Tried {len(restaurants)} restaurants."
            )
        
        # Step 6: Run rank_meals(...) and return the top 5
        logger.info("Ranking meals by relevance score")
        try:
            top_meals = rank_meals(all_meals, top_n=5)
        except Exception as e:
            logger.error(f"Error ranking meals: {str(e)}")
            # If ranking fails, return first 5 meals
            top_meals = all_meals[:5]
        
        # Convert to MealSuggestion format
        meal_suggestions = []
        for meal in top_meals:
            try:
                suggestion = MealSuggestion(
                    meal_name=meal['name'],
                    description=meal['description'],
                    tags=meal['tags'],
                    restaurant_name=meal['restaurant_name'],
                    restaurant_website=meal['restaurant_website']
                )
                meal_suggestions.append(suggestion)
            except Exception as e:
                logger.error(f"Error creating meal suggestion: {str(e)}")
                continue
        
        logger.info(f"Returning {len(meal_suggestions)} top meal recommendations")
        
        # Add metadata about partial results if some restaurants failed
        if failed_restaurants > 0:
            logger.warning(f"Returning partial results: {successful_restaurants} successful, {failed_restaurants} failed")
        
        return meal_suggestions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in recommendation process: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 