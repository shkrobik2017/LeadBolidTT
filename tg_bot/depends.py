from pyrogram import Client

from db.repository import DBRepository
from redis_app.redis_repository import RedisClient
from settings import settings
from tg_bot.tg_handlers import register_handler


async def get_tg_app(repo: DBRepository, redis_client: RedisClient) -> Client:
    global _g_tg_app
    if _g_tg_app is None:
        _g_tg_app = Client(
            name="MainBot",
            session_string=settings.TG_SESSION_STRING,
        )
        await register_handler(_g_tg_app, repo, redis_client)
        return _g_tg_app


_g_tg_app = None
