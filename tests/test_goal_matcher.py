import pytest
from core.goal_matcher import FuzzyGoalMatcher
from core.errors import GoalMatchError

matcher = FuzzyGoalMatcher()

def test_direct_goal():
    result = matcher.match("muscle_gain")
    assert result["goal"] == "muscle_gain"
    assert result["confidence"] == 100

def test_synonym():
    result = matcher.match("bulk phase")
    assert result["goal"] == "muscle_gain"
    assert result["confidence"] == 100

def test_fuzzy():
    result = matcher.match("muscle gaim")
    assert result["goal"] == "muscle_gain"
    assert result["confidence"] >= 80

def test_suggestion():
    with pytest.raises(GoalMatchError) as exc:
        matcher.match("lose weight fast")
    assert "Did you mean" in str(exc.value.suggestion)

def test_keto_synonym():
    result = matcher.match("low carb high fat")
    assert result["goal"] == "keto"
    assert result["confidence"] == 100

def test_vegan_synonym():
    result = matcher.match("plant-based protein")
    assert result["goal"] == "vegan_protein"
    assert result["confidence"] == 100

def test_invalid():
    with pytest.raises(GoalMatchError):
        matcher.match("superman strength") 