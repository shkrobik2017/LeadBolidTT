from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from urllib.parse import quote_plus
from typing import ClassVar

from logger.logger import logger


class MongoDBMotorDBSingletonCreator:
    _instances: ClassVar[dict[tuple[str, str], "MongoDBMotorDBSingletonCreator"]] = {}

    def __new__(
            cls,
            db_url: str,
            host: str,
            db_name: str,
            user: str,
            password: str,
            port: int,
            protocol: str
    ) -> "MongoDBMotorDBSingletonCreator":
        if not db_url:
            user = quote_plus(user)
            password = quote_plus(password)
            db_url = f"{protocol}://{user}:{password}@{host}:{port}"

        if (db_url, db_name) not in cls._instances:
            instance = super().__new__(cls)
            instance._client = AsyncIOMotorClient(db_url)
            instance._db = instance._client[db_name]
            cls._instances[(db_url, db_name)] = instance

        return cls._instances[(db_url, db_name)]

    @property
    def motor_client(self) -> AsyncIOMotorDatabase:
        return self._db

    @classmethod
    def get_instance(cls, db_name: str) -> "MongoDBMotorDBSingletonCreator":
        return next(
            instance for key, instance in cls._instances.items() if key[1] == db_name
        )

    @classmethod
    async def close_all_connections(cls) -> None:
        for (db_url, db_name), instance in list(cls._instances.items()):
            try:
                instance._client.close()
            except Exception as e:
                logger.error(f"Error in closing connection to {db_url}/{db_name}: {e}")
            del cls._instances[(db_url, db_name)]
