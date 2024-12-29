from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient
from routers.group_router.services import check_group_exist_and_create, restart_application

router = APIRouter()


@router.post(
    path="/group/create"
)
async def create_tg_group(
        group_name: str,
        group_id: str,
):
    await run_init_mongodb_beanie()
    repo = DBRepository()
    redis_client = RedisClient()
    await redis_client.connect()

    try:
        logger.info(f"Creating group {group_name=} process is started")
        await check_group_exist_and_create(
            group_name=group_name,
            group_id=group_id,
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
