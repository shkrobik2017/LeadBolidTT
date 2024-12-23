from pyrogram import Client

from settings import settings
from tg_bot.tg_handlers import register_handler


def get_tg_app() -> Client:
    global _g_tg_app
    if _g_tg_app is None:
        _g_tg_app = Client(
            name="MainBot",
            session_string=settings.TG_SESSION_STRING,
        )
        register_handler(_g_tg_app)
        return _g_tg_app


_g_tg_app = None
