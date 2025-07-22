from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, List, Dict

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90, example=40.7128, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180, le=180, example=-74.0060, description="Longitude in decimal degrees")

class MacroOverrides(BaseModel):
    min_calories: Optional[int] = Field(None, ge=0, example=1200)
    max_calories: Optional[int] = Field(None, ge=0, example=2500)
    min_protein: Optional[float] = Field(None, ge=0, example=20)
    max_protein: Optional[float] = Field(None, ge=0, example=200)
    min_carbs: Optional[float] = Field(None, ge=0, example=10)
    max_carbs: Optional[float] = Field(None, ge=0, example=300)
    min_fat: Optional[float] = Field(None, ge=0, example=5)
    max_fat: Optional[float] = Field(None, ge=0, example=100)

class FindMealsRequest(BaseModel):
    location: Location = Field(..., description="User's current location")
    goal: str = Field(..., description="Fitness or nutrition goal (e.g., muscle_gain, keto)")
    radius: float = Field(..., ge=0.5, le=10, example=3, description="Search radius in miles (0.5–10)")
    override_macros: Optional[MacroOverrides] = Field(None, description="Override macro targets")
    flavor_preferences: Optional[List[str]] = Field(None, example=["spicy", "umami"], description="Flavor or cuisine preferences")
    exclude_ingredients: Optional[List[str]] = Field(None, example=["peanuts", "gluten"], description="Ingredients to exclude")

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Goal must be a non-empty string.")
        return v

class FreeformMealSearchRequest(BaseModel):
    location: Location = Field(..., description="User's current location")
    query: str = Field(..., example="low-carb spicy lunch with chicken", description="Natural language meal search query")

class NutritionAnalysisRequest(BaseModel):
    meal_description: str = Field(..., example="Grilled salmon with brown rice and broccoli", description="Meal description for nutrition analysis")
    context: Optional[str] = Field(None, example="keto", description="Optional goal or context for analysis") 