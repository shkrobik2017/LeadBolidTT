from pyrogram import Client

from db.db_setup import run_init_mongodb_beanie
from db.mongodb_client_creator import MongoDBMotorDBSingletonCreator
from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient
from routers.bot_routers.router import router as bot_router
from routers.group_router.router import router as group_router
from scheduler.scheduler_setup import setup_scheduler, scheduler_stopping
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI

from settings import settings
from tg_bot.depends import get_tg_app


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await run_init_mongodb_beanie()
    repo = DBRepository()

    redis_client = RedisClient()
    await redis_client.connect()
    logger.info("Connected to Redis")

    await repo.set_bot_statuses_to_free(redis_client=redis_client)
    logger.info("Bots statuses set to free")

    main_client = await get_tg_app(repo, redis_client)
    logger.info("Telegram client is running")

    await setup_scheduler(main_client, repo, redis_client)
    await main_client.start()
    logger.info("Schedulers are running")

    yield

    await main_client.stop()
    logger.info("Telegram is stopped")

    await scheduler_stopping()
    logger.info("Schedulers stopped")

    await MongoDBMotorDBSingletonCreator.close_all_connections()
    logger.info("Connections to MongoDB closed successful")

    await redis_client.close_con()
    logger.info("Connecting to Redis closed")


app = FastAPI(lifespan=lifespan)
app.include_router(router=bot_router, tags=["Bot Router"])
app.include_router(router=group_router, tags=["Group Router"])



