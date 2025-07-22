from core.fitness_goals import FITNESS_GOALS, GOAL_SYNONYMS
from core.errors import GoalMatchError
from fuzzywuzzy import fuzz
from typing import Dict, Any, List

class FuzzyGoalMatcher:
    def __init__(self):
        self.goals = list(FITNESS_GOALS.keys())
        self.synonyms = GOAL_SYNONYMS
        self.all_terms = list(self.synonyms.keys()) + self.goals

    def match(self, input_str: str) -> Dict[str, Any]:
        input_norm = input_str.strip().lower()
        # Direct synonym match
        if input_norm in self.synonyms:
            canonical = self.synonyms[input_norm]
            return {
                "goal": canonical,
                "confidence": 100,
                "input": input_str,
                "suggestions": []
            }
        # Fuzzy match
        best_score = 0
        best_goal = None
        for term in self.all_terms:
            score = fuzz.token_set_ratio(input_norm, term)
            if score > best_score:
                best_score = score
                best_goal = self.synonyms.get(term, term) if term in self.synonyms else term
        if best_score >= 80:
            return {
                "goal": best_goal,
                "confidence": best_score,
                "input": input_str,
                "suggestions": []
            }
        # Suggest closest goals
        suggestions = self.suggest(input_norm)
        raise GoalMatchError(f"Could not confidently match '{input_str}' to a fitness goal.", suggestion=f"Did you mean: {', '.join(suggestions)}?")

    def suggest(self, input_norm: str) -> List[str]:
        scored = []
        for term in self.all_terms:
            score = fuzz.token_set_ratio(input_norm, term)
            scored.append((term, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [self.synonyms.get(term, term) for term, score in scored[:3] if score > 50] 