from fastapi import HTTPException
from pyrogram.types import Message

from db.db_models import UserModel, MessageModel, BotModel
from logger.logger import logger


class DBRepository:
    async def check_user_exist(self, *, user_id) -> UserModel | None:
        if user := await UserModel.find_one(UserModel.user_id == user_id):
            return user

    async def create_user(self, *, user_id, username) -> UserModel | None:
        try:
            is_user = await self.check_user_exist(user_id=user_id)
            if is_user is None:
                user = UserModel(
                    user_id=user_id,
                    username=username
                )
                await user.create()
                logger.info(f"User {user=} created successful")
                return user
            logger.info(f"User {is_user} already exist!")
            return is_user
        except Exception as ex:
            logger.error(f"An error occurred in saving user to DB: {ex}")
            raise ex

    async def save_message(
            self,
            *,
            user_id: int,
            msg: Message,
            role: str,
            is_image: bool = False,
            bot_id: int | None = None
    ) -> None:
        try:
            match role:
                case "user":
                    message = MessageModel(
                        chat_id=user_id,
                        content=msg.text,
                        role=role,
                        message_id=msg.id
                    )
                case "agent":
                    text = msg.caption if is_image else msg.text
                    message = MessageModel(
                        chat_id=user_id,
                        content=text,
                        role=role,
                        bot_id=bot_id,
                        message_id=msg.id
                    )
                case _:
                    message = MessageModel(
                        chat_id=user_id,
                        content=msg.text,
                        role="unknown"
                    )
            await message.create()
            logger.info(f"Message {message=} created successful")
        except Exception as ex:
            logger.error(f"An error occurred in saving message to DB: {ex}")
            raise ex

    async def get_message_from_db(self, message_id):
        if msg := await MessageModel.find_one(MessageModel.message_id == message_id):
            return msg

    async def check_bot_existing(self, *, bot_name) -> BotModel | None:
        if bot_check := await BotModel.find_one(BotModel.bot_name == bot_name):
            return bot_check

    async def create_new_bot(self, *, bot_name, tg_bot_user_session_string, bot_id) -> BotModel:
        try:
            bot = await self.check_bot_existing(bot_name=bot_name)
            if bot is None:
                bot_model = BotModel(
                    tg_user_bot_session=tg_bot_user_session_string,
                    bot_name=bot_name,
                    bot_id=bot_id
                )
                await bot_model.create()
                return bot_model
            else:
                logger.error(f"Bot {bot_name=} is already existing")
                raise HTTPException(
                    status_code=400,
                    detail={"Already existing": "Bot is already existing"}
                )
        except Exception as ex:
            logger.error(f"An error occurred in creating bot in DB: {ex}")
            raise ex

    async def get_single_bot_from_db(self, bot_id) -> BotModel:
        if bot := await BotModel.find_one(BotModel.bot_id == bot_id):
            return bot

    async def get_all_bots_from_db(self) -> list[BotModel]:
        return await BotModel.find({}).to_list(length=None)
