from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models import PaginationParams, PaginatedResponse, ErrorResponse
from app.core import create_response, create_error_response, validate_object_id
from app.database import get_collection
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health Check"])

@router.get("/", summary="Health Check")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        collection = get_collection("health_check")
        await collection.find_one({})
        
        return create_response(
            message="API is running and database is connected",
            data={
                "status": "healthy",
                "database": "connected",
                "version": settings.api_version
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

@router.get("/db", summary="Database Health Check") 
async def database_health():
    """Database specific health check."""
    try:
        # Test with visitor_logs collection since fingerprints was deprecated
        collection = get_collection("visitor_logs")
        count = await collection.count_documents({})
        
        return create_response(
            message="Database connection is healthy",
            data={
                "database_name": settings.mongodb_database,
                "collection_count": count,
                "status": "connected"
            }
        )
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
