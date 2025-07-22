import structlog
import logging
import sys
from logging.handlers import RotatingFileHandler
import os
import yaml
from core.analytics import AnalyticsTracker
analytics = AnalyticsTracker()
import threading
import time

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
def add_trace_id(logger, method_name, event_dict):
    import contextvars
    trace_id = event_dict.get('trace_id')
    if not trace_id:
        # Try to get from contextvars if available
        try:
            trace_id = contextvars.ContextVar('trace_id').get()
        except Exception:
            trace_id = None
    if trace_id:
        event_dict['trace_id'] = trace_id
    return event_dict

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_trace_id,
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

# In-memory metrics (for demo; use Prometheus client in prod)
_metrics = {
    'request_count': {},  # endpoint: count
    'request_latency': {},  # endpoint: [latencies]
    'cache_hits': 0,
    'cache_misses': 0,
    'gpt_fallbacks': 0,
}
_metrics_lock = threading.Lock()

def inc_request_count(endpoint):
    with _metrics_lock:
        _metrics['request_count'][endpoint] = _metrics['request_count'].get(endpoint, 0) + 1

def add_request_latency(endpoint, ms):
    with _metrics_lock:
        _metrics['request_latency'].setdefault(endpoint, []).append(ms)

def inc_cache_hit():
    with _metrics_lock:
        _metrics['cache_hits'] += 1

def inc_cache_miss():
    with _metrics_lock:
        _metrics['cache_misses'] += 1

def inc_gpt_fallback():
    with _metrics_lock:
        _metrics['gpt_fallbacks'] += 1

def get_prometheus_metrics():
    lines = []
    with _metrics_lock:
        for ep, count in _metrics['request_count'].items():
            lines.append(f'goodeats_request_count{{endpoint="{ep}"}} {count}')
        for ep, lats in _metrics['request_latency'].items():
            if lats:
                avg = sum(lats) / len(lats)
                lines.append(f'goodeats_request_latency_ms_avg{{endpoint="{ep}"}} {avg:.2f}')
        lines.append(f'goodeats_cache_hits { _metrics["cache_hits"] }')
        lines.append(f'goodeats_cache_misses { _metrics["cache_misses"] }')
        lines.append(f'goodeats_gpt_fallbacks { _metrics["gpt_fallbacks"] }')
    return '\n'.join(lines) + '\n'

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