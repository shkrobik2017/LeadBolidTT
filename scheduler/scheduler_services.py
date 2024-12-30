import random
from pathlib import Path
from typing import List
import redis.asyncio as redis
from pyrogram import Client

from db.db_models import BotModel
from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient
from settings import settings

redis = redis.Redis.from_url("redis://redis:6379")


def get_random_photo():
    directory = Path("photos")
    files = [file.name for file in directory.iterdir() if file.is_file()]

    if files:
        random_file = random.choice(files)
        return random_file
    else:
        logger.error("Directory does not have any files")


async def send_tg_photo_message(client):
    get_photo = get_random_photo()
    await client.send_photo(chat_id=settings.TG_GROUP_NAME, photo=f"photos/{get_photo}")


async def send_tg_text_message(client: Client, content: str):
    async with client as cli:
        await cli.send_message(chat_id=settings.TG_GROUP_NAME, text=content)


async def get_random_bots_for_conversation(repo: DBRepository, redis_client: RedisClient):
    bots = await repo.get_many_objects_from_db(model=BotModel, redis=redis_client)
    selected_bots = random.sample(bots, k=2)
    return selected_bots


async def update_client_to_conversation_job(repo: DBRepository, position: str, redis_client: RedisClient) -> BotModel:
    bots: List[BotModel] = await get_random_bots_for_conversation(repo=repo, redis_client=redis_client)
    query = {BotModel.status: "busy", BotModel.is_in_worker: True} \
        if position == "start" \
        else {BotModel.status: "free", BotModel.is_in_worker: False}
    for item in bots:
        await item.set(query)
        item.status = "busy"
    if position == "start":
        serialized_object = [obj.dict() for obj in bots]
        await redis_client.set_key(
            key=f"bots_conversation",
            value=serialized_object,
        )
    elif position == "finish":
        await redis_client.delete_key("bots_conversation")
    return random.choice(bots)


async def set_worker_status(redis_client: RedisClient, status: bool):
    await redis_client.set_key(key="worker_running", value=int(status))


async def update_worker_status(redis_client: RedisClient, status: bool):
    await redis_client.update(key="worker_running", value=int(status))


async def is_worker_running(redis_client: RedisClient):
    status = await redis_client.get_by_key("worker_running")
    logger.info(f"**ConversationWorker**: Worker status is {status}")
    return status == 1
