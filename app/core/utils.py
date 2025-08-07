from fastapi import HTTPException, status
from typing import Any, Dict, List, Optional, Union
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic models."""
    
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string", "format": "objectid"}
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

def create_response(
    success: bool = True,
    message: str = "",
    data: Any = None,
    status_code: int = 200,
    **kwargs
) -> Dict[str, Any]:
    """Create standardized API response."""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code
    }
    
    if data is not None:
        response["data"] = data
    
    response.update(kwargs)
    return response

def create_error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized error response."""
    response = create_response(
        success=False,
        message=message,
        status_code=status_code
    )
    
    if error_code:
        response["error_code"] = error_code
        
    if details:
        response["details"] = details
        
    return response

def handle_database_errors(func):
    """Decorator to handle common database errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database operation failed: {str(e)}"
            )
    return wrapper

def validate_object_id(object_id: str) -> ObjectId:
    """Validate and convert string to ObjectId."""
    try:
        return ObjectId(object_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ObjectId format"
        )
