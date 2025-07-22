from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class FindMealsRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 5.0
    fitness_goal: str
    macros: Optional[Dict[str, float]] = None
    exclusions: Optional[List[str]] = None
    cuisine: Optional[List[str]] = None

class FreeformRequest(BaseModel):
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class NutritionEstimate(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float

class ConfidenceLevel(BaseModel):
    tier: str
    description: str
    source: str
    score: float

class MealCard(BaseModel):
    id: str
    name: str
    restaurant: str
    location: str
    nutrition: NutritionEstimate
    confidence: ConfidenceLevel
    tags: List[str] = []
    price: Optional[float] = None
    image_url: Optional[str] = None

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 