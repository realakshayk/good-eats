import pytest
import asyncio
from parsers.openai_parser import OpenAIParser
from parsers.fallback_parser import FallbackParser

class DummyOpenAIParser(OpenAIParser):
    async def parse_menu(self, raw_text: str):
        # Simulate malformed output
        if "malformed" in raw_text:
            return {"meals": [], "source": "GPT", "confidence": "low", "error": "Failed to parse menu with OpenAI."}
        # Simulate valid output
        return {
            "meals": [{
                "name": "Grilled Chicken Bowl",
                "description": "Grilled chicken with quinoa and vegetables",
                "price": "$12.99",
                "tags": ["high protein", "gluten free"],
                "relevance_score": 0.85,
                "nutrition_estimate": {"calories": 450, "protein": 35, "carbs": 25, "fat": 15}
            }],
            "source": "GPT",
            "confidence": "high"
        }

@pytest.mark.asyncio
async def test_openai_parser_valid():
    parser = DummyOpenAIParser()
    result = await parser.parse_menu("Grilled Chicken Bowl - Grilled chicken with quinoa and vegetables $12.99")
    assert result["meals"]
    assert result["confidence"] == "high"
    assert result["source"] == "GPT"

@pytest.mark.asyncio
async def test_openai_parser_malformed():
    parser = DummyOpenAIParser()
    result = await parser.parse_menu("malformed menu text")
    assert result["confidence"] == "low"
    assert "error" in result

def test_fallback_parser():
    parser = FallbackParser()
    raw = "Grilled Chicken Bowl - Grilled chicken with quinoa and vegetables $12.99\nRandom text\nKeto Avocado Burger - Avocado, beef, cheese $10.50"
    result = parser.parse_menu(raw)
    assert result["meals"]
    assert result["confidence"] == "low"
    assert result["source"] == "fallback"
    assert any("Grilled Chicken" in m["name"] for m in result["meals"]) 