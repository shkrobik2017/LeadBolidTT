from pyrogram import Client, filters
from pyrogram.types import Message, User

from agent.main_agent import MainAgent
from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from settings import settings


def register_handlers(client: Client):
    @client.on_message(filters.private)
    async def handle_text_message(user: User, message: Message):
        print("Message received")
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
            reply = await agent.generate_response(message.text)

            await message.reply(reply)

            await repo.save_message(
                user_id=user_ins.user_id,
                content=reply,
                role="Agent"
            )
        except Exception as ex:
            raise ex


