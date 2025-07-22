from fastapi import APIRouter, Request
from schemas.debug import ApiResponse
from datetime import datetime

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.post("/request-echo", response_model=ApiResponse)
async def request_echo(request: Request):
    body = await request.json()
    return ApiResponse(success=True, data={"echo": body}, error=None, timestamp=datetime.utcnow()) 