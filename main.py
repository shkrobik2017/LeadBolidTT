import asyncio

from pyrogram import Client

from db.mongodb_client_creator import MongoDBMotorDBSingletonCreator
from logger.logger import logger
from routers.bot_routers.router import router
from scheduler.scheduler_setup import setup_scheduler, scheduler_stopping
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI

from tg_bot.depends import get_tg_app


telegram_clients: list[Client] = []


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    scheduler_client = get_tg_app()
    await setup_scheduler(scheduler_client)
    await scheduler_client.start()
    logger.info("All telegram clients are running")

    yield

    await scheduler_client.stop()
    logger.info("Telegram is stopped")
    await scheduler_stopping()
    await MongoDBMotorDBSingletonCreator.close_all_connections()

app = FastAPI(lifespan=lifespan)
app.include_router(router=router, tags=["Bot Router"])



