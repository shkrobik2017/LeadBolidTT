from pyrogram import Client

from logger.logger import logger


async def send_scheduled_message(client: Client, data_to_send: list[dict[str, str]]):
    if client is not None:
        for item in data_to_send:
            await client.send_message(chat_id=item["user_id"], text=item["content"])
            logger.info(f"Message send {item['user_id']}: {item['content']}")
    else:
        logger.error("Telegram client is not initialized")
