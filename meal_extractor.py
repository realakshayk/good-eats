import openai
import json
import logging
import os
from typing import List, Dict, Any
import hashlib
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache file for OpenAI responses
CACHE_FILE = '.gcache_openai.json'
CACHE_DURATION = timedelta(hours=24)

def load_openai_cache():
    """Load cached OpenAI responses."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load OpenAI cache: {e}")
    return {}

def save_openai_cache(cache_data):
    """Save OpenAI responses to cache."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save OpenAI cache: {e}")

def get_openai_cache_key(menu_text: str, goal: str) -> str:
    """Generate cache key for OpenAI request."""
    content = f"{menu_text[:500]}_{goal}"  # Use first 500 chars + goal
    return hashlib.md5(content.encode()).hexdigest()

def is_openai_cache_valid(timestamp_str: str) -> bool:
    """Check if cached OpenAI data is still valid."""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        return datetime.now() - timestamp < CACHE_DURATION
    except Exception:
        return False

def extract_meals_from_menu(menu_text: str, goal: str) -> List[Dict[str, Any]]:
    """
    Extract and analyze meals from restaurant menu text using OpenAI.
    
    Args:
        menu_text: Raw text content from restaurant menu
        goal: User's fitness goal (e.g., "low carb muscle gain", "keto", "high protein")
        
    Returns:
        List of dictionaries containing meal information with:
        - name: Meal name
        - description: Meal description
        - tags: List of nutrition tags
        - relevance_score: Float between 0-1 indicating goal alignment
    """
    
    # Get OpenAI API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Set the API key
    openai.api_key = api_key
    
    # Check cache first
    cache = load_openai_cache()
    cache_key = get_openai_cache_key(menu_text, goal)
    
    if cache_key in cache:
        cached_data = cache[cache_key]
        if is_openai_cache_valid(cached_data['timestamp']):
            logger.info(f"Using cached OpenAI response for goal: {goal}")
            return cached_data['meals']
        else:
            logger.info(f"OpenAI cache expired for goal: {goal}, calling API")
    
    try:
        # Construct the prompt
        system_message = "You are a nutrition AI assistant. Your job is to extract and score meals from a restaurant menu based on a fitness goal."
        
        user_message = f"""
User's goal: {goal}

Restaurant Menu:
{menu_text}

Extract 3–8 individual meals from the menu. For each meal, return the following in JSON:
- name
- description
- tags (e.g. high protein, low carb, vegan, gluten free, etc.)
- relevance_score (0 to 1 based on alignment with user's goal)
"""
        
        logger.info(f"Extracting meals for goal: {goal}")
        logger.info(f"Menu text length: {len(menu_text)} characters")
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        # Extract the assistant's response
        assistant_response = response.choices[0].message.content.strip()
        
        logger.info("Received response from OpenAI")
        
        # Parse the JSON response
        meals = parse_openai_response(assistant_response)
        
        # Cache the result
        cache[cache_key] = {
            'meals': meals,
            'timestamp': datetime.now().isoformat()
        }
        save_openai_cache(cache)
        logger.info(f"Cached OpenAI response for goal: {goal}")
        
        logger.info(f"Successfully extracted {len(meals)} meals")
        return meals
        
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise Exception(f"OpenAI API error: {str(e)}")
    except openai.error.RateLimitError as e:
        logger.error(f"OpenAI rate limit exceeded: {str(e)}")
        raise Exception(f"OpenAI rate limit exceeded: {str(e)}")
    except openai.error.InvalidRequestError as e:
        logger.error(f"OpenAI invalid request: {str(e)}")
        raise Exception(f"OpenAI invalid request: {str(e)}")
    except openai.error.AuthenticationError as e:
        logger.error(f"OpenAI authentication error: {str(e)}")
        raise Exception(f"OpenAI authentication error: {str(e)}")
    except Exception as e:
        logger.error(f"Error extracting meals: {str(e)}")
        raise Exception(f"Failed to extract meals: {str(e)}")

def parse_openai_response(response: str) -> List[Dict[str, Any]]:
    """
    Parse the OpenAI response to extract meal information.
    
    Args:
        response: Raw response from OpenAI
        
    Returns:
        List of meal dictionaries
    """
    
    try:
        # Clean the response - remove markdown code blocks if present
        cleaned_response = response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        
        # Try to parse as JSON array
        try:
            meals_data = json.loads(cleaned_response)
            if isinstance(meals_data, list):
                return validate_and_clean_meals(meals_data)
        except json.JSONDecodeError:
            pass
        
        # If that fails, try to extract JSON from the response
        # Look for JSON array pattern
        import re
        json_pattern = r'\[.*\]'
        json_match = re.search(json_pattern, cleaned_response, re.DOTALL)
        
        if json_match:
            try:
                meals_data = json.loads(json_match.group())
                return validate_and_clean_meals(meals_data)
            except json.JSONDecodeError:
                pass
        
        # If all parsing fails, return empty list
        logger.warning("Could not parse OpenAI response as JSON")
        return []
        
    except Exception as e:
        logger.error(f"Error parsing OpenAI response: {str(e)}")
        return []

def validate_and_clean_meals(meals_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate and clean the extracted meal data.
    
    Args:
        meals_data: Raw meal data from OpenAI
        
    Returns:
        Cleaned and validated meal data
    """
    
    cleaned_meals = []
    
    for meal in meals_data:
        try:
            # Ensure required fields are present
            if not isinstance(meal, dict):
                continue
                
            name = meal.get('name', '').strip()
            if not name:
                continue
            
            # Clean and validate fields
            cleaned_meal = {
                'name': name,
                'description': meal.get('description', '').strip(),
                'tags': validate_tags(meal.get('tags', [])),
                'relevance_score': validate_score(meal.get('relevance_score', 0.5))
            }
            
            cleaned_meals.append(cleaned_meal)
            
        except Exception as e:
            logger.debug(f"Error cleaning meal data: {str(e)}")
            continue
    
    return cleaned_meals

def validate_tags(tags: Any) -> List[str]:
    """
    Validate and clean tags.
    
    Args:
        tags: Raw tags from meal data
        
    Returns:
        List of cleaned tag strings
    """
    
    if isinstance(tags, list):
        return [str(tag).strip().lower() for tag in tags if tag]
    elif isinstance(tags, str):
        # Split comma-separated tags
        return [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
    else:
        return []

def validate_score(score: Any) -> float:
    """
    Validate and clean relevance score.
    
    Args:
        score: Raw score from meal data
        
    Returns:
        Float between 0 and 1
    """
    
    try:
        score_float = float(score)
        return max(0.0, min(1.0, score_float))  # Clamp between 0 and 1
    except (ValueError, TypeError):
        return 0.5  # Default score

def test_meal_extractor():
    """Test function to demonstrate usage."""
    # Sample menu text
    sample_menu = """
    MENU
    
    Appetizers:
    - Grilled Chicken Wings ($12) - Marinated in herbs and spices
    - Caesar Salad ($10) - Fresh romaine, parmesan, croutons
    - Hummus with Pita ($8) - Chickpea dip with warm pita bread
    
    Main Courses:
    - Grilled Salmon ($24) - Atlantic salmon with steamed vegetables
    - Turkey Burger ($16) - Lean ground turkey with whole grain bun
    - Quinoa Bowl ($18) - Quinoa with roasted vegetables and tahini
    - Ribeye Steak ($32) - 12oz prime ribeye with garlic butter
    - Vegetarian Pasta ($14) - Whole wheat pasta with marinara sauce
    
    Sides:
    - Steamed Broccoli ($6)
    - Sweet Potato Fries ($7)
    - Mixed Green Salad ($5)
    """
    
    # Test goals
    test_goals = [
        "low carb muscle gain",
        "keto",
        "high protein",
        "vegetarian"
    ]
    
    for goal in test_goals:
        try:
            print(f"\n{'='*50}")
            print(f"Testing goal: {goal}")
            print(f"{'='*50}")
            
            meals = extract_meals_from_menu(sample_menu, goal)
            
            for i, meal in enumerate(meals, 1):
                print(f"\n{i}. {meal['name']}")
                print(f"   Description: {meal['description']}")
                print(f"   Tags: {', '.join(meal['tags'])}")
                print(f"   Relevance Score: {meal['relevance_score']:.2f}")
                
        except Exception as e:
            print(f"Error testing goal '{goal}': {e}")

if __name__ == "__main__":
    test_meal_extractor() 