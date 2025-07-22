# Test Coverage Reports

## How to Generate Coverage

1. Install coverage tools:
   ```sh
   pip install coverage pytest-cov
   ```
2. Run tests with coverage:
   ```sh
   pytest --cov=.
   ```
3. Generate HTML report:
   ```sh
   coverage html
   # Open htmlcov/index.html in your browser
   ```
4. Generate XML report (for CI/CD badges):
   ```sh
   coverage xml
   ```

## Target
- 90%+ coverage for all core modules
- All new code must include tests 