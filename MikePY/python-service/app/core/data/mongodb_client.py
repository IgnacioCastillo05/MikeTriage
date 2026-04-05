import logging
from pymongo import MongoClient
from app.config.settings import settings

logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        if self._client is None:
            self._client = MongoClient(settings.MONGODB_URI)
            self._db = self._client[settings.MONGODB_DATABASE]
            logger.info(f"Conectado a MongoDB: {settings.MONGODB_DATABASE}")
        return self._db

    def get_db(self):
        if self._db is None:
            self.connect()
        return self._db

    def get_collection(self, name: str):
        return self.get_db()[name]

    def close(self):
        if self._client:
            self._client.close()
            logger.info("MongoDB desconectado")

mongodb = MongoDBClient()