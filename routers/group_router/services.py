import os
import signal

from db.db_models import GroupModel
from db.db_services import get_uuid4_id
from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient


async def check_group_exist_and_create(
        *,
        group_name: str,
        group_prompt_name: str,
        repo: DBRepository,
        redis_client: RedisClient
):
    try:
        bot = await repo.create_object(
            model=GroupModel(
                group_name=group_name,
                group_prompt_name=group_prompt_name
            ),
            filters={"group_name": group_name},
            redis=redis_client
        )
        objects = await GroupModel.find({}).to_list(length=None)
        serialized_object = [obj.dict() for obj in objects]
        await redis_client.update(
            key=f"{GroupModel}_all_objects",
            value=serialized_object
        )

        return bot
    except Exception as ex:
        logger.error(f"Error occurred in checking group existing: {ex}")


def restart_application():
    pid = os.getpid()
    logger.info(f"Restarting application (PID: {pid})...")
    os.kill(pid, signal.SIGTERM)
