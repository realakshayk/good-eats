from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar, Literal, Any
from datetime import datetime
from schemas.errors import ErrorInfo

T = TypeVar("T")

class ApiResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response data payload")
    error: Optional[Any] = Field(None, description="Error details if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp (UTC)")

    @classmethod
    def success_response(cls, data: Any) -> "ApiResponse":
        return cls(success=True, data=data, error=None)

    @classmethod
    def error_response(cls, error: Any) -> "ApiResponse":
        return cls(success=False, data=None, error=error)

class RestaurantSummary(BaseModel):
    name: str = Field(..., example="Fit Kitchen", description="Restaurant name")
    address: str = Field(..., example="123 Main St, New York, NY", description="Restaurant address")
    place_id: str = Field(..., example="ChIJN1t_tDeuEmsRUsoyG83frY4", description="Google Place ID")
    rating: Optional[float] = Field(None, ge=0, le=5, example=4.7, description="Google rating (0–5)")
    distance_miles: Optional[float] = Field(None, ge=0, example=1.2, description="Distance from user in miles")

class NutritionInfo(BaseModel):
    calories: int = Field(..., ge=0, example=450, description="Calories (kcal)")
    protein: float = Field(..., ge=0, example=35, description="Protein (g)")
    carbs: float = Field(..., ge=0, example=25, description="Carbohydrates (g)")
    fat: float = Field(..., ge=0, example=15, description="Fat (g)")
    fiber: Optional[float] = Field(None, ge=0, example=5, description="Fiber (g)")
    sugar: Optional[float] = Field(None, ge=0, example=3, description="Sugar (g)")
    sodium: Optional[float] = Field(None, ge=0, example=400, description="Sodium (mg)")
    confidence_level: Literal["high", "medium", "low"] = Field(..., example="high", description="Confidence in nutrition estimation")
    estimation_origin: Literal["gpt", "rule", "manual"] = Field(..., example="gpt", description="Source of nutrition estimation")

class MealCard(BaseModel):
    name: str = Field(..., example="Grilled Chicken Bowl", description="Meal name")
    description: str = Field(..., example="Grilled chicken with quinoa and vegetables", description="Meal description")
    price: Optional[str] = Field(None, example="$12.99", description="Meal price")
    tags: List[str] = Field(default_factory=list, example=["high protein", "gluten free"], description="Meal tags")
    restaurant: RestaurantSummary = Field(..., description="Summary of the restaurant")
    nutrition: NutritionInfo = Field(..., description="Nutrition information")
    relevance_score: float = Field(..., ge=0, le=1, example=0.85, description="Relevance score (0–1)")
    confidence_level: Literal["high", "medium", "low"] = Field(..., example="high", description="Confidence in meal data")
    estimation_origin: Literal["gpt", "rule", "manual"] = Field(..., example="gpt", description="Source of meal data")

class FindMealsResponse(BaseModel):
    meals: List[MealCard] = Field(..., description="List of meal cards")
    total_results: int = Field(..., ge=0, example=24, description="Total number of results")
    location_summary: str = Field(..., example="Near 123 Main St, New York, NY", description="Summary of search location") 