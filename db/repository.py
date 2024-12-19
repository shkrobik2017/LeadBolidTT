from fastapi import HTTPException

from db.db_models import UserModel, MessageModel, BotModel


class DBRepository:
    roles: dict[str, str] = {"User": "user", "Agent": "agent", "Unknown": "unknown"}

    async def check_user_exist(self, user_id):
        if user := await UserModel.find_one(UserModel.user_id == user_id):
            return user

    async def create_user(self, user_id, username):
        is_user = await self.check_user_exist(user_id)
        if is_user is None:
            user = UserModel(
                user_id=user_id,
                username=username
            )
            await user.create()
            return user
        return is_user

    async def save_message(self, user_id, content, role):
        if role in self.roles.keys():
            message = MessageModel(
                chat_id=user_id,
                content=content,
                role=role
            )
        else:
            message = MessageModel(
                chat_id=user_id,
                content=content,
                role=self.roles["Unknown"]
            )
        await message.create()

    async def check_bot_existing(self, bot_name):
        if bot_check := await BotModel.find_one(BotModel.bot_name == bot_name):
            return bot_check

    async def create_new_bot(self, bot_name, tg_bot_user_session_string):
        bot = await self.check_bot_existing(bot_name)
        if bot is None:
            bot_model = BotModel(
                tg_user_bot_session=tg_bot_user_session_string,
                bot_name=bot_name
            )
            await bot_model.create()
            return bot_model
        else:
            raise HTTPException(
                status_code=400,
                detail={"Already existing": "Bot is already existing"}
            )
