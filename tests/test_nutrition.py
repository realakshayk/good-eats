from tests.utils.mocks import fake_nutrition_info

def test_fake_nutrition_info():
    info = fake_nutrition_info()
    assert info.calories > 0
    assert info.protein > 0
    assert info.carbs > 0
    assert info.fat > 0 