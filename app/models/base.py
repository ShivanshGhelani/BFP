from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime
from app.core import PyObjectId

class BaseDocument(BaseModel):
    """Base model for MongoDB documents."""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={PyObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status_code: int = 200

class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[dict] = None

class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(10, ge=1, le=100, description="Number of records to return")
    sort_field: str = Field("_id", description="Field to sort by")
    sort_order: int = Field(-1, description="Sort order: 1 for ascending, -1 for descending")

class PaginatedResponse(BaseResponse):
    """Paginated response model."""
    data: list = []
    total: int = 0
    skip: int = 0
    limit: int = 0
    has_next: bool = False
    has_prev: bool = False
