import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, User
from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from settings import settings
from tg_bot.tg_services import message_putting_to_queue_process

queue = asyncio.Queue()


def register_handler(client: Client):
    @client.on_message(filters.chat(settings.TG_GROUP_NAME))
    async def handle_group_message(user: User, message: Message):
        repo = DBRepository()
        logger.info("Starting message handler process")

        await run_init_mongodb_beanie()
        try:
            if message.reply_to_message:
                msg = await repo.get_message_from_db(message.reply_to_message_id)
                logger.info(f"{msg=}")
                while True:
                    bot = await repo.get_single_bot_from_db(msg.bot_id)
                    if bot.status == "free":
                        await message_putting_to_queue_process(
                            bot=bot,
                            message=message,
                            queue=queue,
                            repo=repo
                        )

                        break
                    await asyncio.sleep(15)
            else:
                bots = await repo.get_all_bots_from_db()
                bot_ids = [item.bot_id for item in bots]

                if message.from_user.id in bot_ids:
                    logger.info(f"Wrote existing bot: {message.from_user.username=}")
                else:
                    for item in bots:
                        if item.status == "free":
                            await message_putting_to_queue_process(
                                bot=item,
                                message=message,
                                queue=queue,
                                repo=repo
                            )

                            break
        except Exception as ex:
            logger.error(f"An error occurred in handling group message: {ex}")
            raise ex


