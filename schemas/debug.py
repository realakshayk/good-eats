from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 