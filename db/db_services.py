from typing import Annotated
from uuid import UUID, uuid4
from logger.logger import logger

UUIDStr = Annotated[str, lambda v: UUID(v, version=4)]


def get_uuid4_id():
    return str(uuid4())


def error_handler(method):
    async def wrapper(*args, **kwargs):
        try:
            return await method(*args, **kwargs)
        except Exception as ex:
            logger.error(f"Error in {method.__name__}: {ex}")
            raise ex
    return wrapper
