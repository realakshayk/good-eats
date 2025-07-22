import os
import yaml
from config.config import get_settings

print('Active Environment Variables:')
for k, v in os.environ.items():
    if k.startswith('OPENAI') or k.startswith('GOOGLE') or k.startswith('REDIS') or k in ['ENV', 'LOG_LEVEL', 'RATE_LIMIT', 'SCORING_WEIGHTS_PATH', 'SENTRY_DSN', 'MOCK_MODE', 'CACHE_TTL', 'CORS_ORIGINS']:
        print(f'{k}={v}')

print('\nLoaded Config:')
settings = get_settings()
print(settings)

print('\nYAML Configs:')
for fname in ['config/rate_limits.yaml', 'config/cache.yaml', 'config/logging.yaml', 'config/external_services.yaml']:
    try:
        with open(fname) as f:
            print(f'--- {fname} ---')
            print(yaml.safe_load(f))
    except Exception as e:
        print(f'Could not load {fname}:', e) 