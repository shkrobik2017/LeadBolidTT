import asyncio
import time
from pyrogram import Client

from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient
from scheduler.scheduler_services import (
    send_tg_photo_message,
    update_client_to_conversation_job,
    send_tg_text_message,
    set_worker_status, update_worker_status
)
from settings import settings


async def send_scheduled_message(client: Client):
    if client is not None:
        await send_tg_photo_message(client)
        logger.info(f"Periodical message send to {settings.TG_GROUP_NAME}: {time.time()}")
    else:
        logger.error("Telegram client is not initialized")


async def agents_conversation_job(repo: DBRepository, redis_client: RedisClient):
    try:
        bot = await update_client_to_conversation_job(repo=repo, position="start", redis_client=redis_client)
        await set_worker_status(redis_client=redis_client, status=True)

        client = Client(
            name=bot.bot_name,
            session_string=bot.tg_user_bot_session
        )

        await send_tg_text_message(client=client, content="Hello Guys) Let's talk about crypto?")

        await asyncio.sleep(settings.AGENTS_CONVERSATION_DURATION * 60)

        await update_client_to_conversation_job(repo=repo, position="finish", redis_client=redis_client)
        await update_worker_status(status=False, redis_client=redis_client)
    finally:
        await update_client_to_conversation_job(repo=repo, position="finish", redis_client=redis_client)
        await update_worker_status(status=False, redis_client=redis_client)




