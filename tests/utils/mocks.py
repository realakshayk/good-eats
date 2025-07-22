import random
from schemas.responses import NutritionInfo, MealCard, RestaurantSummary

def fake_nutrition_info():
    return NutritionInfo(calories=500, protein=35, carbs=45, fat=15)

def fake_restaurant_summary():
    return RestaurantSummary(
        name="Testaurant",
        address="123 Test St, Test City",
        place_id="test_place_id",
        rating=4.5,
        distance_miles=1.2
    )

def fake_meal_card():
    return MealCard(
        name="Test Meal",
        description="A delicious test meal",
        price="$10.99",
        tags=["test", "mock"],
        restaurant=fake_restaurant_summary(),
        nutrition=fake_nutrition_info(),
        relevance_score=0.9,
        confidence_level="high"
    ) 