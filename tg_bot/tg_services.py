import asyncio
import random
from asyncio import Queue
from pyrogram import Client
from pyrogram.types import Message
from agent.main_agent import MainAgent
from db.db_models import BotModel, UserModel, MessageModel, GroupModel
from db.db_services import error_handler
from db.repository import DBRepository
from logger.logger import logger
from redis_app.redis_repository import RedisClient


async def get_all_tg_group_names(repo: DBRepository, redis: RedisClient):
    group_names = [item.group_name for item in await repo.get_many_objects_from_db(model=GroupModel, redis=redis)]
    return group_names


@error_handler
async def message_putting_to_queue_process(
        *,
        bot: BotModel,
        message: Message,
        queue: Queue,
        repo: DBRepository,
        redis_client: RedisClient
):
    updated_bot = await repo.update_object(
        model=bot,
        filters={"bot_id": bot.bot_id},
        redis=redis_client,
        update_data={BotModel.status: "busy"}
    )
    tg_client = Client(
        name=updated_bot.bot_name,
        session_string=updated_bot.tg_user_bot_session
    )

    await queue.put((message, tg_client))
    logger.info(f"Message putted to queue: {message}")

    await queue_processing(
        queue=queue,
        bot=updated_bot,
        repo=repo,
        redis_client=redis_client
    )


@error_handler
async def handle_text_message(
        client: Client,
        message: Message,
        repo: DBRepository,
        redis_client: RedisClient
):
    logger.info(f"Message received from user: User={message.from_user=}, Message={message.text}")
    user_ins = await repo.create_object(
        model=UserModel(
            user_id=str(message.from_user.id),
            username=message.from_user.username
        ),
        filters={"user_id": str(message.from_user.id)},
        redis=redis_client
    )
    await repo.create_object(
        model=MessageModel(
            user_id=user_ins.user_id,
            content=message.text,
            message_id=message.id,
            role="user"
        ),
        filters={},
        redis=redis_client
    )

    chat_history = await repo.get_chat_history(
        filters={"user_id": user_ins.user_id, "is_summarized": False}
    )

    group = await GroupModel.find_one(GroupModel.group_name == message.chat.username)
    agent = MainAgent()
    generated_reply = await agent.generate_response(
        content=message.text,
        chat_history=chat_history,
        group_prompt_name=group.group_prompt_name,
        redis_client=redis_client,
        summary=user_ins.summary
    )

    reply = await client.send_message(message.chat.username, generated_reply.content)

    await repo.create_object(
        model=MessageModel(
            user_id=user_ins.user_id,
            content=generated_reply.content,
            role="assistant",
            message_id=reply.id,
            bot_id=client.me.id
        ),
        filters={},
        redis=redis_client
    )
    if generated_reply.usage_metadata["input_tokens"] >= 1000:
        await agent.check_tokens_count_in_background(
            redis_client=redis_client,
            chat_history=chat_history,
            repo=repo,
            user_id=user_ins.user_id
        )


@error_handler
async def queue_processing(
        *,
        queue: Queue,
        bot: BotModel,
        repo: DBRepository,
        redis_client: RedisClient
):
    try:
        while True:
            logger.info("Starting queue process")
            message = await queue.get()

            if message is None:
                break

            msg, tg_client = message

            async with tg_client as client:
                await handle_text_message(
                    client=client,
                    message=msg,
                    repo=repo,
                    redis_client=redis_client
                )

                queue.task_done()
                logger.info("Task is done")

                await repo.update_object(
                    model=bot,
                    filters={"bot_id": bot.bot_id},
                    redis=redis_client,
                    update_data={BotModel.status: "free"}
                )
                logger.info("Bot status set to free")
    finally:
        await repo.update_object(
            model=bot,
            filters={"bot_id": bot.bot_id},
            redis=redis_client,
            update_data={BotModel.status: "free"}
        )


@error_handler
async def reply_to_message_process(repo: DBRepository, message: Message, queue: Queue, redis_client: RedisClient):
    msg = await MessageModel.find_one(message_id=message.reply_to_message_id)
    logger.info(f"{msg=}")
    while True:
        bot = await BotModel.find_one(bot_id=msg.bot_id)
        if bot.status == "free":
            await message_putting_to_queue_process(
                bot=bot,
                message=message,
                queue=queue,
                repo=repo,
                redis_client=redis_client
            )

            break
        await asyncio.sleep(15)


@error_handler
async def conversation_worker_process(bots, message, queue, repo, redis_client):
    worker_bots = [
        item for item in bots if item.is_in_worker and item.bot_id != message.from_user.id
    ]
    bot = random.choice(worker_bots)
    await message_putting_to_queue_process(
        bot=bot,
        message=message,
        queue=queue,
        repo=repo,
        redis_client=redis_client
    )


