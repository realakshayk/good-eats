from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rank_meals(meals: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Rank meals by relevance score and goal-aligned tags.
    
    Args:
        meals: List of meal dictionaries from extract_meals_from_menu
        top_n: Number of top meals to return (default: 5)
        
    Returns:
        List of top N meals sorted by relevance_score descending,
        with goal-aligned tags as tiebreaker
    """
    
    if not meals:
        logger.warning("No meals provided for ranking")
        return []
    
    # Define goal-aligned tags and their weights
    goal_aligned_tags = {
        'high_protein': 3,
        'low_carb': 2,
        'keto': 3,
        'low_calorie': 1,
        'vegetarian': 1,
        'vegan': 1,
        'gluten_free': 1,
        'healthy': 1,
        'balanced': 1,
        'lean': 2,
        'protein_rich': 3,
        'carb_free': 2,
        'fat_burning': 2,
        'muscle_building': 3
    }
    
    def calculate_tag_score(meal: Dict[str, Any]) -> int:
        """
        Calculate a score based on goal-aligned tags.
        
        Args:
            meal: Meal dictionary with tags
            
        Returns:
            Integer score based on goal-aligned tags
        """
        tags = meal.get('tags', [])
        if not tags:
            return 0
        
        score = 0
        for tag in tags:
            tag_lower = tag.lower().replace(' ', '_')
            if tag_lower in goal_aligned_tags:
                score += goal_aligned_tags[tag_lower]
        
        return score
    
    def meal_sort_key(meal: Dict[str, Any]) -> tuple:
        """
        Create a sort key for meals: (relevance_score, tag_score).
        
        Args:
            meal: Meal dictionary
            
        Returns:
            Tuple for sorting (higher values first)
        """
        relevance_score = meal.get('relevance_score', 0.0)
        tag_score = calculate_tag_score(meal)
        
        # Return negative values so higher scores come first
        return (-relevance_score, -tag_score)
    
    try:
        # Sort meals by relevance score (descending) and tag score (descending)
        ranked_meals = sorted(meals, key=meal_sort_key)
        
        # Take top N meals
        top_meals = ranked_meals[:top_n]
        
        logger.info(f"Ranked {len(meals)} meals, returning top {len(top_meals)}")
        
        # Log ranking details for debugging
        for i, meal in enumerate(top_meals, 1):
            tag_score = calculate_tag_score(meal)
            logger.debug(f"Rank {i}: {meal['name']} (score: {meal['relevance_score']:.2f}, tags: {tag_score})")
        
        return top_meals
        
    except TypeError as e:
        logger.error(f"Type error in meal ranking: {str(e)}")
        # Return original meals if ranking fails due to type issues
        return meals[:top_n]
    except Exception as e:
        logger.error(f"Error ranking meals: {str(e)}")
        # Return original meals if ranking fails
        return meals[:top_n]

def test_meal_ranker():
    """Test function to demonstrate meal ranking."""
    
    # Sample meals with different relevance scores and tags
    sample_meals = [
        {
            'name': 'Grilled Chicken Breast',
            'description': 'Lean protein with steamed vegetables',
            'tags': ['high_protein', 'low_carb', 'healthy'],
            'relevance_score': 0.9
        },
        {
            'name': 'Salmon with Asparagus',
            'description': 'Omega-3 rich fish with fiber-rich vegetables',
            'tags': ['high_protein', 'low_carb', 'healthy'],
            'relevance_score': 0.9  # Same score as chicken
        },
        {
            'name': 'Quinoa Bowl',
            'description': 'Quinoa with roasted vegetables and tahini',
            'tags': ['vegetarian', 'healthy', 'balanced'],
            'relevance_score': 0.7
        },
        {
            'name': 'Ribeye Steak',
            'description': 'High-fat steak cooked in butter',
            'tags': ['high_protein', 'keto', 'low_carb'],
            'relevance_score': 0.8
        },
        {
            'name': 'Caesar Salad',
            'description': 'Fresh romaine with parmesan and croutons',
            'tags': ['low_calorie', 'healthy'],
            'relevance_score': 0.6
        },
        {
            'name': 'Turkey Burger',
            'description': 'Lean ground turkey with whole grain bun',
            'tags': ['high_protein', 'lean', 'healthy'],
            'relevance_score': 0.85
        },
        {
            'name': 'Bacon-Wrapped Scallops',
            'description': 'High-fat, low-carb seafood option',
            'tags': ['keto', 'high_protein', 'low_carb'],
            'relevance_score': 0.75
        }
    ]
    
    print("Original meals:")
    for i, meal in enumerate(sample_meals, 1):
        print(f"{i}. {meal['name']} (Score: {meal['relevance_score']:.2f}, Tags: {meal['tags']})")
    
    print("\n" + "="*60)
    
    # Test ranking with different top_n values
    for top_n in [3, 5]:
        print(f"\nTop {top_n} ranked meals:")
        ranked_meals = rank_meals(sample_meals, top_n=top_n)
        
        for i, meal in enumerate(ranked_meals, 1):
            tag_score = sum(3 if tag in ['high_protein', 'keto'] else 2 if tag in ['low_carb'] else 1 
                           for tag in meal['tags'])
            print(f"{i}. {meal['name']}")
            print(f"   Score: {meal['relevance_score']:.2f}")
            print(f"   Tags: {', '.join(meal['tags'])} (tag score: {tag_score})")
            print()

def test_tiebreaker():
    """Test the tiebreaker functionality specifically."""
    
    # Meals with same relevance score but different tag alignment
    tie_meals = [
        {
            'name': 'Chicken Breast',
            'description': 'Lean protein',
            'tags': ['high_protein', 'low_carb'],
            'relevance_score': 0.8
        },
        {
            'name': 'Salmon Fillet',
            'description': 'Omega-3 rich fish',
            'tags': ['high_protein', 'low_carb', 'healthy'],
            'relevance_score': 0.8  # Same score as chicken
        },
        {
            'name': 'Steak',
            'description': 'High-protein meat',
            'tags': ['high_protein', 'keto', 'low_carb'],  # More goal-aligned tags
            'relevance_score': 0.8  # Same score as others
        }
    ]
    
    print("Testing tiebreaker with meals having same relevance score:")
    for i, meal in enumerate(tie_meals, 1):
        print(f"{i}. {meal['name']} - Tags: {meal['tags']}")
    
    print("\nRanked order (should prefer steak due to more goal-aligned tags):")
    ranked = rank_meals(tie_meals, top_n=3)
    for i, meal in enumerate(ranked, 1):
        print(f"{i}. {meal['name']} - Tags: {meal['tags']}")

if __name__ == "__main__":
    test_meal_ranker()
    print("\n" + "="*60)
    test_tiebreaker() 