from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import uvicorn
import os
from config.config import get_settings
from routers.meals import router as meals_router
from routers.goals import router as goals_router
from routers.health import router as health_router
from routers.debug import router as debug_router
from routers.metrics import router as metrics_router
from core.auth import get_api_key
from core.ratelimit import RateLimitMiddleware
from core.errors import global_exception_handler
from core.analytics import AnalyticsTracker
import uuid
analytics = AnalyticsTracker()

# Logging setup
logger = structlog.get_logger()

# Middleware for request ID and logging
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get('X-Trace-ID') or str(uuid.uuid4())
        request.state.request_id = request_id
        logger.info("request.start", request_id=request_id, path=request.url.path)
        response = await call_next(request)
        response.headers['X-Trace-ID'] = request_id
        logger.info("request.end", request_id=request_id, status_code=response.status_code)
        return response

# Middleware for metrics (placeholder)
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Add metrics logic here
        response = await call_next(request)
        return response

# Middleware for rate limiting (placeholder)
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Add rate limiting logic here
        response = await call_next(request)
        return response


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Good Eats API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Health endpoints
    @app.get("/api/v1/health/", tags=["Health"])
    async def health():
        return {"status": "ok"}

    @app.get("/api/v1/ready/", tags=["Health"])
    async def ready():
        return {"status": "ready"}

    @app.get("/api/v1/live/", tags=["Health"])
    async def live():
        return {"status": "live"}

    # Routers (all under /api/v1/)
    app.include_router(meals_router, prefix="/api/v1", dependencies=[Depends(get_api_key)])
    app.include_router(goals_router, prefix="/api/v1", dependencies=[Depends(get_api_key)])
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(debug_router, prefix="/api/v1")
    app.include_router(metrics_router, prefix="/api/v1")

    # Override global exception handler
    app.add_exception_handler(Exception, global_exception_handler)

    # Internal docs endpoint (placeholder)
    @app.get("/docs/internal", tags=["Internal"])
    async def internal_docs():
        return {"message": "Prompt design and parsing examples coming soon."}

    @app.get("/metrics", tags=["Monitoring"])
    async def metrics():
        stats = analytics.aggregate()
        return stats

    return app

if __name__ == "__main__":
    uvicorn.run("main:create_app", host="0.0.0.0", port=8000, factory=True, reload=True) 