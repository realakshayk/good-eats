import os
REQUIRED_VARS = [
    'OPENAI_API_KEY', 'GOOGLE_API_KEY', 'REDIS_URI', 'ENV', 'LOG_LEVEL', 'RATE_LIMIT', 'SCORING_WEIGHTS_PATH'
]
missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    print("Missing env vars:", ', '.join(missing))
else:
    print("All required env vars are set.") 