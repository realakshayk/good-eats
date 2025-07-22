from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class FitnessGoal(str, Enum):
    """Supported fitness goals."""
    LOW_CARB_MUSCLE_GAIN = "low_carb_muscle_gain"
    KETO = "keto"
    HIGH_PROTEIN = "high_protein"
    LOW_CALORIE = "low_calorie"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"

class MealTag(str, Enum):
    """Tags for meal analysis."""
    HIGH_PROTEIN = "high_protein"
    LOW_CARB = "low_carb"
    KETO = "keto"
    LOW_CALORIE = "low_calorie"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class RecommendationRequest(BaseModel):
    """Request model for meal recommendations."""
    fitness_goal: FitnessGoal = Field(..., description="User's fitness goal")
    location: str = Field(..., description="Location (e.g., 'Brooklyn, NY')")
    max_recommendations: Optional[int] = Field(5, description="Maximum number of recommendations")

class Restaurant(BaseModel):
    """Restaurant information."""
    place_id: str
    name: str
    address: str
    rating: Optional[float] = None
    price_level: Optional[int] = None
    website: Optional[str] = None
    phone: Optional[str] = None

class MealItem(BaseModel):
    """Individual meal item with analysis."""
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    tags: List[MealTag] = Field(default_factory=list)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    nutrition_notes: Optional[str] = None

class RestaurantWithMeals(BaseModel):
    """Restaurant with its menu items."""
    restaurant: Restaurant
    meals: List[MealItem]

class RecommendationResponse(BaseModel):
    """Response model for meal recommendations."""
    recommendations: List[RestaurantWithMeals]
    total_restaurants_found: int
    total_meals_analyzed: int
    search_location: str
    fitness_goal: FitnessGoal

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0" 