# API Guide

## Base URL
`/api/v1/`

## Authentication
- All endpoints require `X-API-Key` header
- Example: `X-API-Key: test-free-key`

## Endpoints
- `POST /meals/find` — Search meals by location, goal, macros, exclusions
- `POST /meals/freeform` — Freeform meal search (natural language)
- `GET /meals/goals` — List available fitness goals
- `GET /meals/nutrition-rules/{goal}` — Macro rules for a goal
- `GET /meals/confidence-tiers` — Source reliability scoring
- `GET /health/status` — System readiness
- `GET /health/live` — Liveness check
- `GET /health/ready` — Readiness probe

## Example Request
```http
POST /api/v1/meals/find
X-API-Key: test-free-key
Content-Type: application/json

{
  "location": {"lat": 40.7128, "lon": -74.0060},
  "goal": "muscle_gain",
  "radius": 3,
  "override_macros": {"min_calories": 1200, "max_calories": 2500},
  "flavor_preferences": ["spicy"],
  "exclude_ingredients": ["peanuts"]
}
```

## Example Response
```json
{
  "success": true,
  "data": {
    "meals": [
      {
        "name": "Grilled Chicken Bowl",
        "description": "Grilled chicken with quinoa and vegetables",
        "price": "$12.99",
        "tags": ["high protein", "gluten free"],
        "relevance_score": 0.85,
        "confidence_level": "high",
        "nutrition": {"calories": 450, "protein": 35, "carbs": 25, "fat": 15},
        "restaurant": {"name": "Fit Kitchen", "address": "123 Main St", "place_id": "abc123", "rating": 4.7, "distance_miles": 1.2}
      }
    ],
    "total_results": 1,
    "location_summary": "Near 123 Main St, New York, NY"
  },
  "error": null,
  "timestamp": "2025-07-20T10:00:00Z"
}
```

## Error Format
```json
{
  "success": false,
  "error": {
    "type": "InvalidGoalError",
    "message": "Invalid fitness goal provided",
    "details": "Goal 'invalid_goal' not recognized",
    "suggestions": ["muscle_gain", "weight_loss", "keto", "balanced"]
  },
  "timestamp": "2025-07-20T10:30:00Z"
}
```

## OpenAPI/Swagger
- Interactive docs: `/docs`
- Redoc: `/redoc`
- OpenAPI YAML: `/openapi.json`

## B2B Integration
- See `openapi.yaml` for schema reference
- Contact support for partner onboarding 