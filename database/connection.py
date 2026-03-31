"""MongoDB connection manager."""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import MONGODB_URI, MONGODB_DB_NAME


class DatabaseConnection:
    """Manages MongoDB connection."""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern for database connection."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Connect to MongoDB Atlas."""
        try:
            if self._client is None:
                self._client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
                # Verify connection
                self._client.admin.command('ping')
                self._db = self._client[MONGODB_DB_NAME]
                print(f"Connected to MongoDB: {MONGODB_DB_NAME}")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
    
    def get_database(self):
        """Get database instance."""
        if self._db is None:
            connected = self.connect()
            if not connected:
                return None
        return self._db
    
    def is_connected(self):
        """Check if database is connected."""
        return self._db is not None
    
    def close(self):
        """Close database connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("MongoDB connection closed")
    
    def get_companies_collection(self):
        """Get companies collection."""
        database = self.get_database()
        return database.companies if database is not None else None
    
    def get_records_collection(self):
        """Get records collection."""
        database = self.get_database()
        return database.records if database is not None else None


# Global database instance
db = DatabaseConnection()
