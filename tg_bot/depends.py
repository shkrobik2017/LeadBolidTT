from typing import List
from pyrogram import Client

from settings import settings
from tg_bot.tg_clients_data import TELEGRAM_CLIENTS_CONFIG
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


async def create_clients() -> List[Client]:
    clients = []
    for config in TELEGRAM_CLIENTS_CONFIG:
        client = Client(
            name=config["name"],
            api_id=config["api_id"],
            api_hash=config["api_hash"],
            session_string=config["session_string"]
        )
        register_handler(client)
        clients.append(client)
    return clients
