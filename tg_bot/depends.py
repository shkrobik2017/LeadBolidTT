import pyrogram

from settings import settings


def get_tg_app() -> pyrogram.Client:
    global _g_tg_app
    if _g_tg_app is None:
        _g_tg_app = pyrogram.Client(
            name="MainBot",
            session_string=settings.TG_SESSION_STRING,
        )

    return _g_tg_app


_g_tg_app = None
