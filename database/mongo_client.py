import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDBClient:
    _client: AsyncIOMotorClient = None
    _db = None

    @staticmethod
    def get_client():
        if MongoDBClient._client is None:
            load_dotenv()
            uri = os.environ.get("MONGO_URI")
            db_name = os.environ.get("MONGO_DB_NAME")

            if not uri or not db_name:
                raise ValueError("MONGO_URI and MONGO_DB_NAME must be set")

            MongoDBClient._client = AsyncIOMotorClient(uri)
            MongoDBClient._db = MongoDBClient._client[db_name]

        return MongoDBClient._db
