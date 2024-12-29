from db.db_models import BotModel
from db.db_services import get_uuid4_id
from db.repository import DBRepository
from redis_app.redis_repository import RedisClient


async def check_bot_exist_and_create(
        *,
        bot_name: str,
        session_string: str,
        repo: DBRepository,
        bot_id: int,
        redis_client: RedisClient
):
    bot = await repo.create_object(
        model=BotModel(
            bot_name=bot_name,
            tg_user_bot_session=session_string,
            bot_id=bot_id
        ),
        filters={"bot_id": bot_id},
        redis=redis_client
    )

    return bot
