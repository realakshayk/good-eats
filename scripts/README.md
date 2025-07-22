# Good Eats Developer Scripts & Utilities

This directory contains tools for local development, debugging, monitoring, and error diagnosis.

## Debug Scripts
- `test_endpoint.py` — Send live/fake requests to backend endpoints
- `parse_sample_menu.py` — Run OpenAI parser on sample menu text
- `scrape_restaurant.py` — Manual scrape by URL or Place ID
- `profile_discovery.py` — Profile API response times

## Dev Utilities
- `dev_server.sh` — Start local dev server with hot reload
- `validate_env.py` — Ensure all required env vars are present
- `test_api_keys.py` — Verify partner keys and permissions
- `clear_cache.py` — Flush Redis or local fallback

## Monitoring Tools
- `log_tailer.py` — Tail logs/app.log in real time
- (Planned) Streamlit dashboard for rate limit/cache stats

## Usage Examples
```sh
python scripts/test_endpoint.py --url http://localhost:8000/api/v1/meals/find --payload sample_payload.json
python scripts/parse_sample_menu.py --input menu.txt
python scripts/scrape_restaurant.py --url https://example.com/menu --screenshot
bash scripts/dev_server.sh
python scripts/validate_env.py
python scripts/test_api_keys.py
python scripts/clear_cache.py
python scripts/log_tailer.py
```

## Dev Environment
- Use `.env.dev` for local overrides
- Docker Compose and hot reload supported (see main README)

## Tips
- Use `pytest` for running tests
- Use `log_tailer.py` to monitor logs during development
- All scripts are safe to run in local/dev environments 