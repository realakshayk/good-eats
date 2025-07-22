# Troubleshooting Guide

## Common API Errors
- **InvalidGoalError**: The goal provided is not recognized. Check spelling or use `/meals/goals` for valid options.
- **RateLimitError**: Too many requests. Wait and retry, or upgrade your plan.
- **ExternalServiceError**: Upstream API (Google, OpenAI) failed. Try again later.
- **ValidationError**: Input data is missing or malformed. Check required fields and types.
- **NoMealsFoundError**: No meals matched your criteria. Try broadening your search.

## Frontend Issues
- **No results**: Check location, goal, and exclusions. Try a wider radius.
- **API errors**: See error banner for details. Use browser dev tools for network logs.
- **Map not loading**: Ensure internet connection and browser compatibility.

## Deployment
- **Backend not reachable**: Check FastAPI server logs and port settings.
- **Redis unavailable**: Ensure Redis is running and URI is correct.
- **OpenAI/Google API errors**: Check API keys and quotas.

## Debugging Tips
- Use `scripts/log_tailer.py` to monitor logs in real time
- Use `scripts/test_endpoint.py` to test API endpoints
- Check `.env` and config files for missing or incorrect values 