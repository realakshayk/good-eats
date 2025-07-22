from fastapi import APIRouter
from schemas.health import HealthStatus, ApiResponse
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/status", response_model=ApiResponse)
async def health_status():
    return ApiResponse(success=True, data={"status": "ok"}, error=None, timestamp=datetime.utcnow())

@router.get("/live", response_model=ApiResponse)
async def health_live():
    return ApiResponse(success=True, data={"status": "live"}, error=None, timestamp=datetime.utcnow())

@router.get("/ready", response_model=ApiResponse)
async def health_ready():
    return ApiResponse(success=True, data={"status": "ready"}, error=None, timestamp=datetime.utcnow()) 