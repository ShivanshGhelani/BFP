from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from app.models import PaginationParams, PaginatedResponse
from app.core import create_response, create_error_response, validate_object_id, BaseService
from app.database import get_collection
import logging

logger = logging.getLogger(__name__)

class BaseRouter:
    """Base router class with common CRUD operations."""
    
    def __init__(self, collection_name: str, tag: str):
        self.collection_name = collection_name
        self.router = APIRouter(prefix=f"/{collection_name}", tags=[tag])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup common CRUD routes."""
        
        @self.router.get("/", summary=f"Get all {self.collection_name}")
        async def get_all(
            pagination: PaginationParams = Depends()
        ):
            try:
                collection = get_collection(self.collection_name)
                service = BaseService(collection)
                
                # Get paginated data
                data = await service.get_all(
                    skip=pagination.skip,
                    limit=pagination.limit,
                    sort_field=pagination.sort_field,
                    sort_order=pagination.sort_order
                )
                
                # Get total count
                total = await service.count()
                
                # Create paginated response
                return PaginatedResponse(
                    data=data,
                    total=total,
                    skip=pagination.skip,
                    limit=pagination.limit,
                    has_next=pagination.skip + pagination.limit < total,
                    has_prev=pagination.skip > 0,
                    message=f"Successfully retrieved {self.collection_name}"
                )
                
            except Exception as e:
                logger.error(f"Error getting {self.collection_name}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve {self.collection_name}"
                )
        
        @self.router.get("/{item_id}", summary=f"Get {self.collection_name} by ID")
        async def get_by_id(item_id: str):
            try:
                object_id = validate_object_id(item_id)
                collection = get_collection(self.collection_name)
                service = BaseService(collection)
                
                item = await service.get_by_id(object_id)
                if not item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{self.collection_name.capitalize()} not found"
                    )
                
                return create_response(
                    data=item,
                    message=f"Successfully retrieved {self.collection_name}"
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting {self.collection_name} by ID: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve {self.collection_name}"
                )
        
        @self.router.delete("/{item_id}", summary=f"Delete {self.collection_name}")
        async def delete_item(item_id: str):
            try:
                object_id = validate_object_id(item_id)
                collection = get_collection(self.collection_name)
                service = BaseService(collection)
                
                # Check if item exists
                existing_item = await service.get_by_id(object_id)
                if not existing_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{self.collection_name.capitalize()} not found"
                    )
                
                # Delete the item
                deleted = await service.delete(object_id)
                if not deleted:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to delete {self.collection_name}"
                    )
                
                return create_response(
                    message=f"Successfully deleted {self.collection_name}"
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting {self.collection_name}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete {self.collection_name}"
                )

def create_crud_router(collection_name: str, tag: str) -> APIRouter:
    """Factory function to create CRUD router for a collection."""
    base_router = BaseRouter(collection_name, tag)
    return base_router.router
