from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

# Create database instance
database = Database()

async def connect_to_mongo():
    """Create database connection on application startup."""
    try:
        logger.info("Connecting to MongoDB...")
        database.client = AsyncIOMotorClient(settings.mongodb_url)
        database.database = database.client[settings.mongodb_database]
        
        # Test the connection
        await database.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB database: {settings.mongodb_database}")
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close database connection on application shutdown."""
    try:
        if database.client:
            database.client.close()
            logger.info("MongoDB connection closed.")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if database.database is None:
        raise RuntimeError("Database is not initialized. Call connect_to_mongo() first.")
    return database.database

def get_collection(collection_name: str):
    """Get a collection from the database."""
    db = get_database()
    return db[collection_name]
