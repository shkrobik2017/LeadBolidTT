from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient
from routers.bot_routers.services import check_bot_exist_and_create

router = APIRouter()


@router.post(
    path="/bot/create"
)
async def create_bot(
        bot_name: str,
        tg_session_string: str,
        bot_tg_id: int,
):
    await run_init_mongodb_beanie()
    repo = DBRepository()
    redis_client = RedisClient()
    await redis_client.connect()

    try:
        logger.info(f"Creating bot {bot_name=} process is started")
        await check_bot_exist_and_create(
            bot_name=bot_name,
            session_string=tg_session_string,
            repo=repo,
            bot_id=bot_tg_id,
            redis_client=redis_client
        )
        return {"Successful": "Bot created successfully"}
    except Exception as ex:
        logger.error(f"An error occurred in creating bot: {ex}")
        raise HTTPException(
            status_code=500,
            detail={"Eternal error": "Something went wrong in creating bot"}
        )
