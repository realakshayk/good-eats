# Architecture Overview

## System Diagram
```mermaid
flowchart TD
    subgraph Frontend
        A1[Streamlit App]
        A2[Static SPA]
    end
    subgraph API Layer
        B1[FastAPI Backend]
    end
    subgraph Services
        S1[Meal Discovery]
        S2[Google Places]
        S3[Menu Scraper]
        S4[AI Parser]
        S5[Nutrition Estimator]
        S6[Scoring Engine]
    end
    subgraph Core
        C1[Goal Matcher]
        C2[Auth & Rate Limit]
        C3[Error Handling]
        C4[Caching]
    end
    subgraph Infra
        I1[Redis]
        I2[OpenAI]
        I3[Playwright]
        I4[Google API]
        I5[File Fallback]
    end
    A1 --> B1
    A2 --> B1
    B1 --> S1
    S1 --> S2
    S1 --> S3
    S1 --> S4
    S1 --> S5
    S1 --> S6
    S2 --> I4
    S3 --> I3
    S4 --> I2
    S5 --> I2
    S1 --> C1
    S1 --> C2
    S1 --> C3
    S1 --> C4
    C4 --> I1
    C4 --> I5
```

## Folder Structure
```
api/v1/         # Versioned API routes
services/       # Core service logic
core/           # Business rules, auth, rate limiting
schemas/        # Pydantic models
models/         # Internal data representations
scoring/        # Scoring logic
parsers/        # Menu parsing (AI, fallback)
scrapers/       # Scraping logic
utils/          # Utilities (logging, env)
config/         # Configs, YAMLs
static/         # SPA frontend
logs/           # Logs
assets/         # Images/icons
scripts/        # Dev/debug tools
docs/           # Documentation
``` 