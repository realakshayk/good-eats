import openai
import asyncio
import os
import json
from typing import Dict, Any, Optional
from config.config import get_settings
from schemas.responses import NutritionInfo
import structlog

logger = structlog.get_logger()

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '../data/nutrient_templates.json')

SYSTEM_PROMPT = """
You are a nutrition estimation assistant. Given a meal name and description, estimate the nutrition as JSON:
{"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": null, "sugar": null, "sodium": null}
"""

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Grilled Chicken Bowl: Grilled chicken with quinoa and vegetables"
    },
    {
        "role": "assistant",
        "content": '{"calories": 450, "protein": 35, "carbs": 25, "fat": 15, "fiber": 5, "sugar": 3, "sodium": 400}'
    }
]

class NutritionEstimator:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = "gpt-3.5-turbo-1106"
        self.temperature = 0
        self.max_tokens = 128
        self.max_retries = 3
        self.templates = self._load_templates()

    def _load_templates(self):
        try:
            with open(TEMPLATE_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warn("nutrition.templates.load_failed", error=str(e))
            return {}

    async def estimate(self, name: str, description: str) -> Dict[str, Any]:
        # Try GPT first
        for attempt in range(self.max_retries):
            try:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *FEW_SHOT_EXAMPLES,
                    {"role": "user", "content": f"{name}: {description}"}
                ]
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"},
                    timeout=20
                )
                content = response.choices[0].message.content
                data = self._safe_json_load(content)
                if data and "calories" in data:
                    return {
                        "nutrition": data,
                        "origin": "gpt",
                        "confidence": "high"
                    }
            except Exception as e:
                logger.warn("nutrition.gpt.retry", error=str(e), attempt=attempt)
                await asyncio.sleep(2 ** attempt)
        # Fallback: rule-based
        return self._rule_based_estimate(name, description)

    def _rule_based_estimate(self, name: str, description: str) -> Dict[str, Any]:
        text = f"{name} {description}".lower()
        for key, tpl in self.templates.items():
            if key in text:
                # Use average of range
                nutrition = {
                    "calories": int(sum(tpl["calories"]) / 2),
                    "protein": float(sum(tpl["protein"]) / 2),
                    "carbs": float(sum(tpl["carbs"]) / 2),
                    "fat": float(sum(tpl["fat"]) / 2),
                    "fiber": None, "sugar": None, "sodium": None
                }
                return {
                    "nutrition": nutrition,
                    "origin": "rule",
                    "confidence": "medium"
                }
        # Manual fallback
        return {
            "nutrition": {
                "calories": 400, "protein": 20, "carbs": 40, "fat": 10, "fiber": None, "sugar": None, "sodium": None
            },
            "origin": "manual",
            "confidence": "low"
        }

    def _safe_json_load(self, content: str) -> Any:
        try:
            return json.loads(content)
        except Exception:
            try:
                return json.loads(content.replace("'", '"'))
            except Exception:
                return None 