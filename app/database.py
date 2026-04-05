"""MongoDB database connection management"""
from app.core.config import get_settings

# Global MongoDB connection and collection handles
_db_client = None
_db = None
namespaces_collection = None
app_metadata_collection = None
migration_data_collection = None
aggregated_cache_collection = None


class DatabaseConnectionError(RuntimeError):
    """Raised when MongoDB is unavailable or not initialized."""
    pass


async def connect_to_mongo() -> None:
    """
    Initialize MongoDB connection.
    Called during application startup.
    """
    global _db_client, _db
    global namespaces_collection, app_metadata_collection, migration_data_collection, aggregated_cache_collection

    settings = get_settings()

    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        _db_client = AsyncIOMotorClient(
            settings.mongodb_uri,
            maxPoolSize=settings.mongodb_max_pool_size,
        )
        _db = _db_client[settings.mongodb_db_name]

        namespaces_collection = _db["namespaces"]
        app_metadata_collection = _db["app_metadata"]
        migration_data_collection = _db["migration_data"]
        aggregated_cache_collection = _db["aggregated_namespace_cache"]

        # Verify connection and create indexes
        await _db_client.admin.command("ping")
        await namespaces_collection.create_index(
            "name",
            name="idx_namespace_name",
            unique=True,
            background=True,
        )
        await aggregated_cache_collection.create_index(
            "cache_ts",
            name="idx_aggregated_cache_ttl",
            expireAfterSeconds=600,
            background=True,
        )

        print(f"✓ Connected to MongoDB: {settings.mongodb_db_name}")
    except Exception as e:
        print(f"⚠ MongoDB connection warning: {e}")
        print("  Application will run without database. Configure MongoDB to enable persistence.")


async def close_mongo_connection() -> None:
    """
    Close MongoDB connection.
    Called during application shutdown.
    """
    global _db_client, _db
    global namespaces_collection, app_metadata_collection, migration_data_collection, aggregated_cache_collection

    if _db_client:
        try:
            _db_client.close()
            print("Closed MongoDB connection")
        except Exception as e:
            print(f"Error closing connection: {e}")
        finally:
            _db_client = None
            _db = None
            namespaces_collection = None
            app_metadata_collection = None
            migration_data_collection = None
            aggregated_cache_collection = None


def get_database():
    """Get the MongoDB database instance"""
    if _db is None:
        raise DatabaseConnectionError("Database not initialized. Configure MongoDB connection in .env")
    return _db
