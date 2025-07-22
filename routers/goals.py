from fastapi import APIRouter, Path
from schemas.goals import GoalDefinition, NutritionRule, ApiResponse
from datetime import datetime

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.get("/", response_model=ApiResponse)
async def get_goals():
    return ApiResponse(success=True, data={"goals": []}, error=None, timestamp=datetime.utcnow())

@router.get("/nutrition-rules/{goal}", response_model=ApiResponse)
async def get_nutrition_rules(goal: str = Path(...)):
    return ApiResponse(success=True, data={"rules": []}, error=None, timestamp=datetime.utcnow()) 