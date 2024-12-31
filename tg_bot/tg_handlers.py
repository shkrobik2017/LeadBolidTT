import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, User

from db.db_services import error_handler
from redis_app.redis_repository import RedisClient
from db.db_models import BotModel
from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from scheduler.scheduler_services import is_worker_running
from settings import settings
from tg_bot.tg_services import message_putting_to_queue_process, reply_to_message_process, conversation_worker_process, \
    get_all_tg_group_names

queue = asyncio.Queue()


async def register_handler(client: Client, repo: DBRepository, redis_client: RedisClient):
    group_names = await get_all_tg_group_names(repo=repo, redis=redis_client)
    logger.info(f"**Telegram**: Groups fetched successful: {group_names=}")

    @error_handler
    @client.on_message(filters.chat(group_names))
    async def handle_group_message(user: User, message: Message):
        logger.info("**Telegram**: Starting message handler process")

        await run_init_mongodb_beanie()
        await asyncio.sleep(2)

        if message.reply_to_message:
            await reply_to_message_process(
                repo=repo,
                message=message,
                queue=queue,
                redis_client=redis_client
            )
        else:
            bots = await repo.get_many_objects_from_db(model=BotModel, redis=redis_client)
            bot_ids = [item.bot_id for item in bots]

            if message.from_user.id in bot_ids:
                logger.info(f"**Telegram**: Wrote existing bot: {message.from_user.phone_number=}")
                if await is_worker_running(redis_client=redis_client) and message.chat.username == settings.TG_GROUP_NAME:
                    bots = [BotModel(**item) for item in await redis_client.get_by_key("bots_conversation")]
                    await conversation_worker_process(
                        bots=bots,
                        message=message,
                        queue=queue,
                        repo=repo,
                        redis_client=redis_client
                    )
            else:
                free_bot = next((item for item in bots if item.status == "free"), None)
                if free_bot is not None and free_bot.status == "free":
                    await message_putting_to_queue_process(
                        bot=free_bot,
                        message=message,
                        queue=queue,
                        repo=repo,
                        redis_client=redis_client
                    )
