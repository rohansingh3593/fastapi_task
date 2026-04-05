"""MongoDB database connection management"""
from app.core.config import get_settings

# Global database instance
_db_client = None
_db = None


async def connect_to_mongo() -> None:
    """
    Initialize MongoDB connection.
    Called during application startup.
    """
    global _db_client, _db
    
    settings = get_settings()
    
    try:
        from motor.motor_asyncio import AsyncClient
        _db_client = AsyncClient(settings.mongodb_uri)
        _db = _db_client[settings.mongodb_db_name]
        
        # Verify connection
        await _db_client.admin.command("ping")
        print(f"✓ Connected to MongoDB: {settings.mongodb_db_name}")
    except Exception as e:
        print(f"⚠ MongoDB connection warning: {e}")
        print(f"  Application will run without database. Configure MongoDB to enable persistence.")


async def close_mongo_connection() -> None:
    """
    Close MongoDB connection.
    Called during application shutdown.
    """
    global _db_client, _db
    
    if _db_client:
        try:
            _db_client.close()
            print("Closed MongoDB connection")
        except Exception as e:
            print(f"Error closing connection: {e}")
        finally:
            _db_client = None
            _db = None


def get_database():
    """Get the MongoDB database instance"""
    if _db is None:
        raise RuntimeError("Database not initialized. Configure MongoDB connection in .env")
    return _db
