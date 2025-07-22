# Development Guide

## Onboarding
- Clone the repo and install dependencies (`pip install -r requirements.txt`)
- Copy `.env.template` to `.env` and fill in secrets
- Start dev server: `bash scripts/dev_server.sh` or `uvicorn main:create_app --factory --reload`
- Run tests: `pytest`

## Folder Structure
See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Best Practices
- Use Pydantic models for all request/response schemas
- Keep business logic in `services/`, not in API routes
- Use `core/` for reusable business rules, auth, and error handling
- Add new goals/parsers by extending `core/fitness_goals.py` and `parsers/`
- Use `utils/logger.py` for all logging

## Testing & CI
- Unit and integration tests in `tests/`
- Use `pytest`, `pytest-asyncio`, `pytest-mock`
- Mock external APIs with `respx`, `vcrpy`, or `httpretty`
- Add new tests for all new features and bugfixes
- Integrate with CI/CD for automated test runs

## Contribution & PR Checklist
- [ ] Add/Update tests for new code
- [ ] Update docs if API or logic changes
- [ ] Run `pytest` and ensure all tests pass
- [ ] Use clear, descriptive commit messages
- [ ] Follow code style and linting guidelines 