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
        group_id: str,
        repo: DBRepository,
        redis_client: RedisClient
):
    try:
        bot = await repo.create_object(
            model=GroupModel(
                group_name=group_name,
                group_id=group_id
            ),
            filters={"group_id": group_id},
            redis=redis_client
        )

        return bot
    except Exception as ex:
        logger.error(f"Error occurred in checking group existing: {ex}")


def restart_application():
    pid = os.getpid()
    print(f"Restarting application (PID: {pid})...")
    os.kill(pid, signal.SIGTERM)
