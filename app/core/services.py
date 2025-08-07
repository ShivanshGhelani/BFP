from typing import List, Optional, Any, Dict
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
import logging
from app.core.utils import handle_database_errors
from app.database.connection import get_collection
from datetime import datetime
from app.core.location_utils import get_location_from_coordinates  # Import reverse geocode function
import re

logger = logging.getLogger(__name__)

class BaseService:
    """Base service class for common database operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    @handle_database_errors
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document."""
        result = await self.collection.insert_one(data)
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        return created_doc

    @handle_database_errors
    async def get_by_id(self, object_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        return await self.collection.find_one({"_id": object_id})

    @handle_database_errors
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        sort_field: str = "_id",
        sort_order: int = DESCENDING,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get all documents with pagination and filtering."""
        query = filter_dict or {}
        cursor = self.collection.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @handle_database_errors
    async def update(self, object_id: ObjectId, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update document by ID."""
        await self.collection.update_one({"_id": object_id}, {"$set": data})
        return await self.collection.find_one({"_id": object_id})

    @handle_database_errors
    async def delete(self, object_id: ObjectId) -> bool:
        """Delete document by ID."""
        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0

    @handle_database_errors
    async def count(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching filter."""
        query = filter_dict or {}
        return await self.collection.count_documents(query)

    @handle_database_errors
    async def exists(self, filter_dict: Dict[str, Any]) -> bool:
        """Check if document exists."""
        count = await self.collection.count_documents(filter_dict, limit=1)
        return count > 0

    @handle_database_errors
    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document by filter."""
        return await self.collection.find_one(filter_dict)

    @handle_database_errors
    async def find_many(
        self, 
        filter_dict: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort_field: str = "_id",
        sort_order: int = DESCENDING
    ) -> List[Dict[str, Any]]:
        """Find many documents by filter."""
        cursor = self.collection.find(filter_dict).sort(sort_field, sort_order).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

async def log_visitor_profile(ip: str, profile: dict, real_ip: str = None):
    collection = get_collection("visitor_logs")
    visitor_id = profile.get('visitor_id')
    visit_count = profile.get('visit_count', 1)
    user_agent = profile.get('navigator', {}).get('ua', '')
    browser = detect_browser(user_agent)
    gps = profile.get('loc', {}).get('gps')
    address = None
    if gps and 'latitude' in gps and 'longitude' in gps:
        location_data = await get_location_from_coordinates(gps['latitude'], gps['longitude'])
        address = location_data.get('combined') or location_data.get('display_name')
        gps['address'] = address
    # Upsert logic: increment visit_count for existing visitor_id
    doc_update = {
        "profile": profile,
        "browser": browser,
        "created_at": datetime.utcnow()
    }
    if visitor_id:
        result = await collection.find_one_and_update(
            {"visitor_id": visitor_id},
            {"$set": doc_update, "$inc": {"visit_count": 1}},
            upsert=True,
            return_document=True
        )
    else:
        doc_update["visit_count"] = visit_count
        await collection.insert_one(doc_update)

def detect_browser(user_agent):
    # Simple user agent parser for major browsers
    if 'Edg/' in user_agent:
        return 'Edge'
    elif 'OPR/' in user_agent or 'Opera' in user_agent:
        return 'Opera'
    elif 'Chrome/' in user_agent and 'Chromium' not in user_agent:
        return 'Chrome'
    elif 'Firefox/' in user_agent:
        return 'Firefox'
    elif 'Safari/' in user_agent and 'Chrome/' not in user_agent:
        return 'Safari'
    elif 'Chromium' in user_agent:
        return 'Chromium'
    else:
        return 'Other'
