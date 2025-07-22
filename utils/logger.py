import structlog
import logging
import sys
from logging.handlers import RotatingFileHandler
import os
import yaml
from core.analytics import AnalyticsTracker
analytics = AnalyticsTracker()

LOGGING_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/logging.yaml')

# Load logging config
def load_logging_config():
    try:
        with open(LOGGING_CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {"level": "INFO", "log_to_file": False, "file_path": "logs/app.log", "max_bytes": 1048576, "backup_count": 5}

config = load_logging_config()

# Set up root logger
level = getattr(logging, config.get("level", "INFO"))
logging.basicConfig(level=level, stream=sys.stdout, format="%(message)s")

# Rotating file handler
if config.get("log_to_file", False):
    file_handler = RotatingFileHandler(
        config.get("file_path", "logs/app.log"),
        maxBytes=config.get("max_bytes", 1048576),
        backupCount=config.get("backup_count", 5)
    )
    file_handler.setLevel(level)
    logging.getLogger().addHandler(file_handler)

# Structlog config
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Sentry integration stub
def init_sentry():
    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        try:
            import sentry_sdk
            sentry_sdk.init(dsn=dsn, traces_sample_rate=1.0)
        except ImportError:
            pass

def log_goal_search(goal, params):
    analytics.log_event('goal_search', {'goal': goal, 'params': params})

def log_meal_view(meal_id, user_id=None):
    analytics.log_event('meal_view', {'meal_id': meal_id, 'user_id': user_id})

def log_meal_favorite(meal_id, user_id=None):
    analytics.log_event('meal_favorite', {'meal_id': meal_id, 'user_id': user_id})

def log_api_timing(endpoint, ms):
    analytics.log_event('api_timing', {'endpoint': endpoint, 'ms': ms})

def log_gpt_usage(tokens, response_type):
    analytics.log_event('gpt_usage', {'tokens': tokens, 'response_type': response_type})

def log_scraper_fallback(url, reason):
    analytics.log_event('scraper_fallback', {'url': url, 'reason': reason}) 