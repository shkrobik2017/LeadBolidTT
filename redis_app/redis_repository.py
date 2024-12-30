import json

import redis.asyncio as redis
from typing import Optional, Any, Union
from logger.logger import logger
from settings import settings

GetReturnType = Union[str, list[dict], dict]


class RedisClient:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        """Initialize the Redis connection."""
        try:
            self.redis = await redis.Redis.from_url(self.redis_url, decode_responses=True)
        except Exception as ex:
            logger.error(f"**Redis**: Failed to connect to Redis: {ex}")
            raise ex

    async def close_con(self):
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()

    async def set_key(self, key: str, value: Any, ex: Optional[int] = None):
        """Set a key-value pair in Redis with an optional expiration time."""
        try:
            serialized_value = json.dumps(value) if value is not str else value
            await self.redis.set(key, serialized_value, ex=ex)
            logger.info(f"**Redis**: Set key '{key}' in Redis.")
        except Exception as ex:
            logger.error(f"**Redis**: Failed to set key '{key}' in Redis: {ex}")
            raise ex

    async def update(self, key: str, value: Any):
        """Update the value of an existing key in Redis."""
        try:
            if await self.check_exist(key):
                await self.set_key(key, value)
                logger.info(f"**Redis**: Updated key '{key}' in Redis.")
            else:
                logger.warning(f"**Redis**: Key '{key}' does not exist in Redis. Cannot update.")
        except Exception as ex:
            logger.error(f"**Redis**: Failed to update key '{key}' in Redis: {ex}")
            raise ex

    async def get_by_key(self, key: str) -> GetReturnType | None:
        """Get a value from Redis by key."""
        try:
            value = await self.redis.get(key)
            if value:
                logger.info(f"**Redis**: Retrieved key '{key}' from Redis.")
                deserialized_value = json.loads(value)
                return deserialized_value
            logger.info(f"**Redis**: Cache with {key=} not found")
            return None
        except Exception as ex:
            logger.error(f"**Redis**: Failed to get key '{key}' from Redis: {ex}")
            raise ex

    async def delete_key(self, key: str):
        """Delete a key from Redis."""
        try:
            await self.redis.delete(key)
            logger.info(f"**Redis**: Deleted key '{key}' from Redis.")
        except Exception as ex:
            logger.error(f"**Redis**: Failed to delete key '{key}' from Redis: {ex}")
            raise ex

    async def check_exist(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            exists = await self.redis.exists(key)
            logger.info(f"**Redis**: Checked existence of key '{key}' in Redis: {bool(exists)}")
            return bool(exists)
        except Exception as ex:
            logger.error(f"**Redis**: Failed to check existence of key '{key}' in Redis: {ex}")
            raise ex


