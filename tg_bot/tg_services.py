from asyncio import Queue

from pyrogram import Client
from pyrogram.types import User, Message

from agent.main_agent import MainAgent
from db.db_models import BotModel
from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from settings import settings


async def handle_text_message(client: Client, message: Message):
    logger.info(f"Message received from user: User={message.from_user=}, Message={message.text}")
    try:
        await run_init_mongodb_beanie()

        repo = DBRepository()
        user_ins = await repo.create_user(
            user_id=str(message.from_user.id),
            username=message.from_user.username
        )
        await repo.save_message(
            user_id=user_ins.user_id,
            content=message.text,
            role="User"
        )

        agent = MainAgent()
        reply = await agent.generate_response(content=message.text)

        await client.send_message(settings.TG_GROUP_NAME, reply)

        await repo.save_message(
            user_id=user_ins.user_id,
            content=reply,
            role="Agent"
        )
    except Exception as ex:
        logger.error(f"An error occurred in TG message handler: {ex}")
        raise ex


async def handle_text_message_with_image_reply(client: Client, message: Message):
    logger.info(f"Message received from user: User={message.from_user=}, Message={message.text}")
    try:
        await run_init_mongodb_beanie()

        repo = DBRepository()
        user_ins = await repo.create_user(
            user_id=str(message.from_user.id),
            username=message.from_user.username
        )
        await repo.save_message(
            user_id=user_ins.user_id,
            content=message.text,
            role="User"
        )

        # agent = MainAgent()
        # reply = await agent.generate_response(content=message.text)

        # await message.reply(reply)
        await client.send_photo(settings.TG_GROUP_NAME, "photos/293578.jpg")
        reply = "Photo images.jpg send to the user"
        await repo.save_message(
            user_id=user_ins.user_id,
            content=reply,
            role="Agent"
        )
    except Exception as ex:
        logger.error(f"An error occurred in TG message handler: {ex}")
        raise ex


async def queue_processing(queue: Queue, bot_id):
    while True:
        logger.info("Starting queue process")
        message = await queue.get()

        if message is None:
            break

        msg, tg_client = message

        async with tg_client as client:
            await handle_text_message(
                client=client,
                message=msg
            ) if client.name.lower().startswith("text") \
                else await handle_text_message_with_image_reply(
                client=client,
                message=msg
            )

            queue.task_done()
            logger.info("Task is done")

            bot = await BotModel.get(bot_id)
            await bot.set({BotModel.status: "free"})

            logger.info("Bot status set to free")


