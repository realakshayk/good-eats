from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class GoalDefinition(BaseModel):
    name: str
    description: str
    recommended_macros: Dict[str, float]

class NutritionRule(BaseModel):
    goal: str
    macro_ranges: Dict[str, List[float]]
    notes: Optional[str] = None

class ConfidenceLevel(BaseModel):
    tier: str
    description: str
    source: str
    score: float

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 