from fastapi import APIRouter
from schemas.health import HealthStatus
from schemas.responses import ApiResponse
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/status", response_model=ApiResponse)
async def health_status():
    return ApiResponse.success_response({"status": "ok"})

@router.get("/live", response_model=ApiResponse)
async def health_live():
    return ApiResponse.success_response({"status": "live"})

@router.get("/ready", response_model=ApiResponse)
async def health_ready():
    return ApiResponse.success_response({"status": "ready"}) 