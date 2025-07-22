import re
from typing import List, Dict, Any

FOOD_KEYWORDS = [
    "grilled", "crispy", "tofu", "chicken", "beef", "salad", "bowl", "burger", "quinoa", "avocado", "vegan", "steak", "rice", "pasta", "shrimp", "fish", "egg", "cheese", "wrap", "plate"
]

class FallbackParser:
    def parse_menu(self, raw_text: str) -> Dict[str, Any]:
        lines = raw_text.split("\n")
        meals = []
        for line in lines:
            if any(word in line.lower() for word in FOOD_KEYWORDS) and len(line) > 10:
                name = line.split("-")[0].strip()
                desc = line.split("-", 1)[1].strip() if "-" in line else ""
                price_match = re.search(r"\$\d+[\.\d+]*", line)
                price = price_match.group(0) if price_match else None
                meals.append({
                    "name": name,
                    "description": desc,
                    "price": price,
                    "tags": [],
                    "relevance_score": 0.5,
                    "nutrition_estimate": {"calories": None, "protein": None, "carbs": None, "fat": None}
                })
        return {
            "meals": meals,
            "source": "fallback",
            "confidence": "low"
        } 