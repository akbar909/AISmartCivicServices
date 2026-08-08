"""
MongoDB connection and Beanie ODM initialization.
Uses Motor async driver with Beanie document models.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import get_settings

logger = logging.getLogger(__name__)

# Patch Motor's AsyncIOMotorClient to support append_metadata for Beanie ODM compatibility
if not hasattr(AsyncIOMotorClient, "append_metadata"):
    AsyncIOMotorClient.append_metadata = lambda self, *a, **kw: (
        self.delegate.append_metadata(*a, **kw)
        if hasattr(self.delegate, "append_metadata")
        else None
    )

# Global client reference for cleanup
_client: AsyncIOMotorClient | None = None


async def init_db():
    """Initialize MongoDB connection and Beanie ODM.
    
    Fails fast with a clear error if the database is unreachable.
    """
    global _client
    settings = get_settings()

    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,  # Fail fast if unreachable
        )
        # Force a connection check
        await _client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise RuntimeError(
            f"Could not connect to MongoDB at the configured URI. "
            f"Please check MONGODB_URI in your .env file. Error: {e}"
        )

    # Import document models here to avoid circular imports
    from app.models.user import User
    from app.models.complaint import Complaint
    from app.models.department import Department
    from app.models.notification import Notification

    await init_beanie(
        database=_client[settings.DATABASE_NAME],
        document_models=[User, Complaint, Department, Notification],
    )
    logger.info(f"Beanie initialized with database: {settings.DATABASE_NAME}")


async def close_db():
    """Close MongoDB connection."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")
