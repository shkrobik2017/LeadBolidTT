import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, User

from agent.main_agent import MainAgent
from db.db_models import BotModel
from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from settings import settings
from tg_bot.tg_services import queue_processing

queue = asyncio.Queue()


def register_handler(client: Client):
    @client.on_message(filters.chat(settings.TG_GROUP_NAME))
    async def handle_group_message(user: User, message: Message):
        try:
            logger.info("Starting message handler process")
            await run_init_mongodb_beanie()
            bots = await BotModel.find({}).to_list(length=None)
            bot_ids = [item.bot_id for item in bots]
            for item in bots:
                if message.from_user.id in bot_ids:
                    logger.info(f"Wrote existing bot: {item=}")
                    break

                if item.status == "free":
                    await item.set({BotModel.status: "busy"})
                    tg_client = Client(
                        name=item.bot_name,
                        session_string=item.tg_user_bot_session
                    )

                    await queue.put((message, tg_client))
                    logger.info(f"Message putted to queue: {message}")

                    await queue_processing(queue, item.id)

                    break
        except Exception as ex:
            logger.error(f"An error occurred in handling group message: {ex}")
            raise ex


