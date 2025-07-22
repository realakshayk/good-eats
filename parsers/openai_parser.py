import openai
import asyncio
import os
from typing import List, Dict, Any
from config.config import get_settings
import structlog
import time

logger = structlog.get_logger()

SYSTEM_PROMPT = """
You are a menu parsing assistant. Output ONLY valid JSON in the following format:
{
  "meals": [
    {
      "name": "...",
      "description": "...",
      "price": "$...",
      "tags": ["..."],
      "relevance_score": 0.0,
      "nutrition_estimate": {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
      }
    }
  ]
}
"""

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Grilled Chicken Bowl - Grilled chicken with quinoa and vegetables $12.99"
    },
    {
        "role": "assistant",
        "content": '{"meals": [{"name": "Grilled Chicken Bowl", "description": "Grilled chicken with quinoa and vegetables", "price": "$12.99", "tags": ["high protein", "gluten free"], "relevance_score": 0.85, "nutrition_estimate": {"calories": 450, "protein": 35, "carbs": 25, "fat": 15}}]}'
    }
]

class OpenAIParser:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = "gpt-3.5-turbo-1106"
        self.temperature = 0
        self.max_retries = 3
        self.rate_limit_per_min = 60
        self.last_call = 0
        self.min_interval = 60 / self.rate_limit_per_min

    async def parse_menu(self, raw_text: str) -> Dict[str, Any]:
        for attempt in range(self.max_retries):
            await self._respect_rate_limit()
            try:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *FEW_SHOT_EXAMPLES,
                    {"role": "user", "content": raw_text}
                ]
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    response_format={"type": "json_object"},
                    timeout=30
                )
                content = response.choices[0].message.content
                data = self._safe_json_load(content)
                if data and "meals" in data:
                    return {
                        "meals": data["meals"],
                        "source": "GPT",
                        "confidence": "high"
                    }
            except Exception as e:
                logger.warn("openai.parse.retry", error=str(e), attempt=attempt)
                await asyncio.sleep(2 ** attempt)
        return {
            "meals": [],
            "source": "GPT",
            "confidence": "low",
            "error": "Failed to parse menu with OpenAI."
        }

    async def _respect_rate_limit(self):
        now = time.time()
        wait = self.min_interval - (now - self.last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        self.last_call = time.time()

    def _safe_json_load(self, content: str) -> Any:
        import json
        try:
            return json.loads(content)
        except Exception:
            # Try to fix common issues
            try:
                return json.loads(content.replace("'", '"'))
            except Exception:
                return None 