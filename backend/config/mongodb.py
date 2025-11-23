"""
MongoDB Connection Utility

Provides MongoDB client and database access for the application.
"""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from django.conf import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """Singleton MongoDB connection manager."""
    
    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._connect()
    
    def _connect(self):
        """Establish MongoDB connection."""
        try:
            mongo_settings = settings.MONGODB_SETTINGS
            connection_string = f"mongodb://{mongo_settings['host']}:{mongo_settings['port']}"
            
            self._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test connection
            self._client.admin.command('ping')
            
            self._db = self._client[mongo_settings['database']]
            logger.info(f"✅ MongoDB connected: {mongo_settings['database']}")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self._client = None
            self._db = None
    
    @property
    def db(self) -> Optional[Database]:
        """Get database instance."""
        if self._db is None:
            self._connect()
        return self._db
    
    @property
    def client(self) -> Optional[MongoClient]:
        """Get MongoDB client."""
        if self._client is None:
            self._connect()
        return self._client
    
    def get_collection(self, name: str) -> Optional[Collection]:
        """Get a collection by name."""
        if self.db is not None:
            return self.db[name]
        return None
    
    def close(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")

# Global instance
mongo_db = MongoDBConnection()

def get_mongo_db() -> Optional[Database]:
    """Get MongoDB database instance."""
    return mongo_db.db

def get_collection(name: str) -> Optional[Collection]:
    """Get MongoDB collection."""
    return mongo_db.get_collection(name)
