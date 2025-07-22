from pydantic import BaseModel, Field
from typing import Optional, List

class ErrorInfo(BaseModel):
    type: str = Field(..., example="ValidationError", description="Type of error")
    message: str = Field(..., example="Invalid latitude value", description="Error message")
    details: Optional[str] = Field(None, example="Latitude must be between -90 and 90.", description="Detailed error info")
    suggestions: Optional[List[str]] = Field(None, example=["Check your coordinates", "Try a different location"], description="Suggestions for resolving the error")

class ValidationError(ErrorInfo):
    type: str = Field(default="ValidationError", example="ValidationError")

class ServiceError(ErrorInfo):
    type: str = Field(default="ServiceError", example="ServiceError") 