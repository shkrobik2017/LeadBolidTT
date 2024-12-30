from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient
from routers.group_router.depends import POSSIBLE_PROMPT_NAMES
from routers.group_router.services import check_group_exist_and_create, restart_application

router = APIRouter()


@router.post(
    path="/group/create"
)
async def create_tg_group(
        group_name: str,
        group_prompt_name: str
):
    if group_prompt_name not in POSSIBLE_PROMPT_NAMES:
        logger.error("Provided invalid group prompt name")
        raise HTTPException(
            status_code=400,
            detail={
                "Bad Request": f"Provided invalid group prompt name: {group_prompt_name}."
                               f"\nValid prompt names: crypto, financial"
            }
        )
    await run_init_mongodb_beanie()
    repo = DBRepository()
    redis_client = RedisClient()
    await redis_client.connect()

    try:
        logger.info(f"Creating group {group_name=} process is started")
        await check_group_exist_and_create(
            group_name=group_name,
            group_prompt_name=group_prompt_name,
            repo=repo,
            redis_client=redis_client
        )
        restart_application()
        return {"Successful": "Group created successfully"}
    except Exception as ex:
        logger.error(f"An error occurred in creating group: {ex}")
        raise HTTPException(
            status_code=500,
            detail={"Eternal error": "Something went wrong in creating group"}
        )
