from typing import Dict, Any, Optional
from core.fitness_goals import FITNESS_GOALS
from schemas.responses import NutritionInfo

def analyze_goal_fit(nutrition: NutritionInfo, goal: str) -> Dict[str, Any]:
    goal_def = FITNESS_GOALS.get(goal)
    if not goal_def:
        return {"match_score": 0, "tags": ["unknown goal"], "reason": "Goal not found"}
    macros = goal_def["macros"]
    cal_range = goal_def["calories"]
    score = 1.0
    tags = []
    # Calories
    if not (cal_range[0] <= nutrition.calories <= cal_range[1]):
        tags.append("calorie mismatch")
        score -= 0.3
    # Protein
    p_pct = nutrition.protein * 4 / max(nutrition.calories, 1)
    if not (macros["protein"][0] <= p_pct <= macros["protein"][1]):
        tags.append("protein mismatch")
        score -= 0.2
    # Carbs
    c_pct = nutrition.carbs * 4 / max(nutrition.calories, 1)
    if not (macros["carbs"][0] <= c_pct <= macros["carbs"][1]):
        tags.append("carb mismatch")
        score -= 0.2
    # Fat
    f_pct = nutrition.fat * 9 / max(nutrition.calories, 1)
    if not (macros["fat"][0] <= f_pct <= macros["fat"][1]):
        tags.append("fat mismatch")
        score -= 0.2
    score = max(0, min(1, score))
    return {"match_score": score, "tags": tags, "reason": None if score == 1 else "Macros/calories out of goal range"} 