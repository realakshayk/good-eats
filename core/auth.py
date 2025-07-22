import yaml
import os
from fastapi import Header, HTTPException, Request, status, Depends
from typing import Optional
import structlog

logger = structlog.get_logger()

API_KEYS_PATH = os.path.join(os.path.dirname(__file__), '../config/api_keys.yaml')

def load_api_keys():
    try:
        with open(API_KEYS_PATH, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('api_keys', {})
    except Exception as e:
        logger.error("auth.api_keys.load_failed", error=str(e))
        return {}

API_KEYS = load_api_keys()

def reload_api_keys():
    global API_KEYS
    API_KEYS = load_api_keys()
    logger.info("auth.api_keys.reloaded")

async def get_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key"), request: Request = None):
    if not x_api_key or x_api_key not in API_KEYS:
        logger.warn("auth.failed", request_id=getattr(request.state, 'request_id', None))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    plan = API_KEYS[x_api_key]['plan']
    request.state.api_plan = plan
    request.state.api_key = x_api_key
    logger.info("auth.success", api_key=x_api_key, plan=plan, request_id=getattr(request.state, 'request_id', None))
    return x_api_key

# CLI utility for key rotation
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="API Key Rotation Utility")
    parser.add_argument('--reload', action='store_true', help='Reload API keys from config')
    args = parser.parse_args()
    if args.reload:
        reload_api_keys()
        print("API keys reloaded.") 