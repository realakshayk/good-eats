from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import structlog

logger = structlog.get_logger()

class InvalidGoalError(Exception):
    def __init__(self, message: str, details: str = None, suggestions=None):
        self.message = message
        self.details = details
        self.suggestions = suggestions or []

class NoMealsFoundError(Exception):
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details

class ExternalServiceError(Exception):
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details

class ValidationError(Exception):
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details

class RateLimitError(Exception):
    def __init__(self, message: str, details: str = None, retry_after: int = None):
        self.message = message
        self.details = details
        self.retry_after = retry_after

class ParsingError(Exception):
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details

class GoalMatchError(Exception):
    def __init__(self, message: str, suggestion: str = "Try a different goal."):
        self.message = message
        self.suggestion = suggestion

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
    timestamp: datetime = datetime.utcnow()
    trace_id: str = None

async def global_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, 'request_id', None)
    error_type = exc.__class__.__name__
    error_dict = {"type": error_type, "message": str(getattr(exc, 'message', str(exc))), "details": getattr(exc, 'details', None)}
    if hasattr(exc, 'suggestions'):
        error_dict["suggestions"] = getattr(exc, 'suggestions')
    logger.error("unhandled_exception", error=error_dict, trace_id=trace_id)
    status_code = status.HTTP_400_BAD_REQUEST
    if error_type == "RateLimitError":
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif error_type == "ExternalServiceError":
        status_code = status.HTTP_502_BAD_GATEWAY
    elif error_type == "ParsingError":
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif error_type == "NoMealsFoundError":
        status_code = status.HTTP_404_NOT_FOUND
    elif error_type == "ValidationError":
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    response = JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=error_dict, trace_id=trace_id).dict()
    )
    if trace_id:
        response.headers["X-Trace-ID"] = trace_id
    return response 