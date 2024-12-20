from pyrogram import Client

from db.mongodb_client_creator import MongoDBMotorDBSingletonCreator
from logger.logger import logger
from routers.bot_routers.router import router
from scheduler.scheduler_setup import setup_scheduler, scheduler_stopping
from tg_bot.depends import get_tg_app
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI

from tg_bot.tg_handlers import register_handlers

telegram_client: dict[str, Client] = {}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    client = get_tg_app()
    telegram_client["client"] = client
    register_handlers(client)
    await setup_scheduler(client)

    await client.start()
    logger.info("Telegram is running")

    yield

    await client.stop()
    logger.info("Telegram is stopped")
    await scheduler_stopping()
    await MongoDBMotorDBSingletonCreator.close_all_connections()

app = FastAPI(lifespan=lifespan)
app.include_router(router=router, tags=["Bot Router"])



