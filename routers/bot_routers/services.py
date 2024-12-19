from db.repository import DBRepository


async def check_bot_exist_and_create(bot_name: str, session_string: str, repo: DBRepository):
    bot = await repo.create_new_bot(
        bot_name=bot_name,
        tg_bot_user_session_string=session_string
    )

    return bot
