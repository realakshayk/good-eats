import openai
from typing import List, Dict, Any
from app.models import MealItem, MealTag, FitnessGoal
from app.utils.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class LLMAnalyzerService:
    """Service for analyzing menu items using OpenAI LLM."""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
    
    async def analyze_menu_items(self, menu_items: List[Dict[str, Any]], fitness_goal: FitnessGoal) -> List[MealItem]:
        """
        Analyze menu items and tag them based on fitness goals.
        
        Args:
            menu_items: List of menu items from scraping
            fitness_goal: User's fitness goal
            
        Returns:
            List of MealItem objects with tags and analysis
        """
        if not menu_items:
            return []
        
        try:
            # Prepare prompt for LLM
            prompt = self._create_analysis_prompt(menu_items, fitness_goal)
            
            # Call OpenAI API
            response = await self._call_openai(prompt)
            
            # Parse response
            analyzed_items = self._parse_llm_response(response, menu_items)
            
            logger.info(f"Analyzed {len(analyzed_items)} menu items for {fitness_goal}")
            return analyzed_items
            
        except Exception as e:
            logger.error(f"Error analyzing menu items: {str(e)}")
            return []
    
    def _create_analysis_prompt(self, menu_items: List[Dict[str, Any]], fitness_goal: FitnessGoal) -> str:
        """
        Create a prompt for the LLM to analyze menu items.
        
        Args:
            menu_items: List of menu items
            fitness_goal: User's fitness goal
            
        Returns:
            Formatted prompt string
        """
        # Create menu items text
        menu_text = ""
        for i, item in enumerate(menu_items[:20]):  # Limit to 20 items for token efficiency
            menu_text += f"{i+1}. {item['name']}"
            if item.get('description'):
                menu_text += f" - {item['description']}"
            if item.get('price'):
                menu_text += f" (${item['price']})"
            menu_text += "\n"
        
        # Define available tags
        available_tags = [tag.value for tag in MealTag]
        
        prompt = f"""
You are a nutrition expert analyzing restaurant menu items for a user with the fitness goal: {fitness_goal.value}.

Available nutrition tags: {', '.join(available_tags)}

Analyze each menu item and return a JSON array with the following structure for each item:
{{
    "index": <item_number>,
    "name": "<item_name>",
    "tags": ["tag1", "tag2"],
    "confidence_score": <0.0-1.0>,
    "nutrition_notes": "<brief nutrition analysis>"
}}

Guidelines:
- HIGH_PROTEIN: Items with significant protein content (meat, fish, eggs, legumes)
- LOW_CARB: Items with minimal carbohydrates (avoid bread, pasta, rice, potatoes)
- KETO: Very low carb, high fat items
- LOW_CALORIE: Items under 400 calories typically
- VEGETARIAN: No meat, fish, or poultry
- VEGAN: No animal products
- GLUTEN_FREE: No wheat, barley, rye
- HEALTHY: Generally nutritious options
- UNHEALTHY: High in unhealthy fats, sugars, or processed ingredients

Focus on items that align with the user's goal: {fitness_goal.value}

Menu items:
{menu_text}

Return only the JSON array, no additional text.
"""
        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """
        Call OpenAI API with the analysis prompt.
        
        Args:
            prompt: Analysis prompt
            
        Returns:
            LLM response
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert. Provide accurate, helpful analysis in JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
    
    def _parse_llm_response(self, response: str, original_items: List[Dict[str, Any]]) -> List[MealItem]:
        """
        Parse the LLM response and create MealItem objects.
        
        Args:
            response: LLM response string
            original_items: Original menu items
            
        Returns:
            List of MealItem objects
        """
        try:
            # Clean response and extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Parse JSON
            analysis_data = json.loads(response)
            
            meal_items = []
            for item_analysis in analysis_data:
                try:
                    index = item_analysis.get('index', 0) - 1
                    if 0 <= index < len(original_items):
                        original_item = original_items[index]
                        
                        # Convert string tags to MealTag enum
                        tags = []
                        for tag_str in item_analysis.get('tags', []):
                            try:
                                tag = MealTag(tag_str)
                                tags.append(tag)
                            except ValueError:
                                logger.debug(f"Invalid tag: {tag_str}")
                        
                        meal_item = MealItem(
                            name=original_item['name'],
                            description=original_item.get('description'),
                            price=original_item.get('price'),
                            tags=tags,
                            confidence_score=item_analysis.get('confidence_score', 0.5),
                            nutrition_notes=item_analysis.get('nutrition_notes')
                        )
                        meal_items.append(meal_item)
                        
                except Exception as e:
                    logger.debug(f"Error parsing item analysis: {str(e)}")
                    continue
            
            return meal_items
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return []
    
    async def filter_by_goal(self, meal_items: List[MealItem], fitness_goal: FitnessGoal) -> List[MealItem]:
        """
        Filter meal items based on fitness goal relevance.
        
        Args:
            meal_items: List of analyzed meal items
            fitness_goal: User's fitness goal
            
        Returns:
            Filtered list of meal items
        """
        goal_tag_mapping = {
            FitnessGoal.LOW_CARB_MUSCLE_GAIN: [MealTag.HIGH_PROTEIN, MealTag.LOW_CARB],
            FitnessGoal.KETO: [MealTag.KETO, MealTag.LOW_CARB],
            FitnessGoal.HIGH_PROTEIN: [MealTag.HIGH_PROTEIN],
            FitnessGoal.LOW_CALORIE: [MealTag.LOW_CALORIE],
            FitnessGoal.VEGETARIAN: [MealTag.VEGETARIAN],
            FitnessGoal.VEGAN: [MealTag.VEGAN],
            FitnessGoal.GLUTEN_FREE: [MealTag.GLUTEN_FREE]
        }
        
        target_tags = goal_tag_mapping.get(fitness_goal, [])
        
        # Score items based on goal alignment
        scored_items = []
        for item in meal_items:
            score = 0
            for tag in item.tags:
                if tag in target_tags:
                    score += 1
                elif tag == MealTag.HEALTHY:
                    score += 0.5
                elif tag == MealTag.UNHEALTHY:
                    score -= 1
            
            # Only include items with positive scores
            if score > 0:
                scored_items.append((item, score))
        
        # Sort by score and return top items
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in scored_items[:10]]  # Return top 10 