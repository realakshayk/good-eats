FITNESS_GOALS = {
    "muscle_gain": {
        "name": "muscle_gain",
        "description": "High protein (30–40%), 2500–3500 cal, moderate carbs/fats",
        "calories": [2500, 3500],
        "macros": {"protein": [0.3, 0.4], "carbs": [0.3, 0.4], "fat": [0.2, 0.3]},
        "synonyms": ["muscle building", "bulk phase", "gaining", "mass up"]
    },
    "weight_loss": {
        "name": "weight_loss",
        "description": "1500–2000 cal, 25–30% protein, low carbs, moderate fats",
        "calories": [1500, 2000],
        "macros": {"protein": [0.25, 0.3], "carbs": [0.2, 0.35], "fat": [0.3, 0.4]},
        "synonyms": ["fat loss", "cutting phase", "lean down"]
    },
    "keto": {
        "name": "keto",
        "description": "5–10% carbs, 70–80% fat, moderate protein, 1800–2200 cal",
        "calories": [1800, 2200],
        "macros": {"protein": [0.15, 0.25], "carbs": [0.05, 0.1], "fat": [0.7, 0.8]},
        "synonyms": ["keto diet", "low carb high fat"]
    },
    "balanced": {
        "name": "balanced",
        "description": "2000–2500 cal with balanced macros (30/40/30)",
        "calories": [2000, 2500],
        "macros": {"protein": [0.3, 0.3], "carbs": [0.4, 0.4], "fat": [0.3, 0.3]},
        "synonyms": []
    },
    "athletic_endurance": {
        "name": "athletic_endurance",
        "description": "3000–4000 cal, higher carbs (50–60%), moderate protein/fat",
        "calories": [3000, 4000],
        "macros": {"protein": [0.15, 0.2], "carbs": [0.5, 0.6], "fat": [0.2, 0.3]},
        "synonyms": ["endurance", "marathon training"]
    },
    "vegan_protein": {
        "name": "vegan_protein",
        "description": "2000–2400 cal, high plant protein, low/medium fat",
        "calories": [2000, 2400],
        "macros": {"protein": [0.25, 0.35], "carbs": [0.4, 0.5], "fat": [0.2, 0.3]},
        "synonyms": ["vegan", "plant-based protein"]
    }
}

GOAL_SYNONYMS = {}
for goal, data in FITNESS_GOALS.items():
    for syn in data["synonyms"]:
        GOAL_SYNONYMS[syn.lower()] = goal
    GOAL_SYNONYMS[goal.replace("_", " ")] = goal
    GOAL_SYNONYMS[goal] = goal 