from fastapi import APIRouter, HTTPException

from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from routers.bot_routers.services import check_bot_exist_and_create

router = APIRouter()


@router.post(
    path="/bot/create"
)
async def create_bot(
        bot_name: str,
        tg_session_string: str
):
    await run_init_mongodb_beanie()
    repo = DBRepository()

    try:
        logger.info(f"Creating bot {bot_name=} process is started")
        await check_bot_exist_and_create(
            bot_name=bot_name,
            session_string=tg_session_string,
            repo=repo
        )
        return {"Successful": "Bot created successfully"}
    except Exception as ex:
        logger.error(f"An error occurred in creating bot: {ex}")
        raise HTTPException(
            status_code=500,
            detail={"Eternal error": "Something went wrong in creating bot"}
        )
