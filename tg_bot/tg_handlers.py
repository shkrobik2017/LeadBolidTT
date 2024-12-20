from pyrogram import Client, filters
from pyrogram.types import Message, User

from agent.main_agent import MainAgent
from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger


def register_handlers(client: Client):
    @client.on_message(filters.private)
    async def handle_text_message(user: User, message: Message):
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

            await message.reply(reply)

            await repo.save_message(
                user_id=user_ins.user_id,
                content=reply,
                role="Agent"
            )
        except Exception as ex:
            logger.error(f"An error occurred in TG message handler: {ex}")
            raise ex


