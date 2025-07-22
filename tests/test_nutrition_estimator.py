import pytest
import asyncio
from services.nutrition_estimator import NutritionEstimator
from core.nutrition_utils import analyze_goal_fit
from schemas.responses import NutritionInfo

class DummyNutritionEstimator(NutritionEstimator):
    async def estimate(self, name, description):
        if "burger" in name.lower():
            return {"nutrition": {"calories": 700, "protein": 30, "carbs": 50, "fat": 35}, "origin": "rule", "confidence": "medium"}
        if "unknown" in name.lower():
            return {"nutrition": {"calories": 400, "protein": 20, "carbs": 40, "fat": 10}, "origin": "manual", "confidence": "low"}
        return {"nutrition": {"calories": 450, "protein": 35, "carbs": 25, "fat": 15}, "origin": "gpt", "confidence": "high"}

@pytest.mark.asyncio
async def test_gpt_estimate():
    est = DummyNutritionEstimator()
    result = await est.estimate("Grilled Chicken Bowl", "Grilled chicken with quinoa and vegetables")
    assert result["origin"] == "gpt"
    assert result["confidence"] == "high"
    assert result["nutrition"]["calories"] == 450

@pytest.mark.asyncio
async def test_rule_based_estimate():
    est = DummyNutritionEstimator()
    result = await est.estimate("Burger", "Beef burger with cheese")
    assert result["origin"] == "rule"
    assert result["confidence"] == "medium"
    assert 600 <= result["nutrition"]["calories"] <= 800

@pytest.mark.asyncio
async def test_manual_fallback():
    est = DummyNutritionEstimator()
    result = await est.estimate("Unknown Meal", "Mystery ingredients")
    assert result["origin"] == "manual"
    assert result["confidence"] == "low"
    assert result["nutrition"]["calories"] == 400

def test_goal_fit_analyzer():
    info = NutritionInfo(calories=700, protein=30, carbs=50, fat=35)
    result = analyze_goal_fit(info, "muscle_gain")
    assert "calorie mismatch" not in result["tags"]
    assert 0 <= result["match_score"] <= 1
    info2 = NutritionInfo(calories=1200, protein=10, carbs=100, fat=50)
    result2 = analyze_goal_fit(info2, "keto")
    assert "carb mismatch" in result2["tags"] or "fat mismatch" in result2["tags"] 