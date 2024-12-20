from asyncio import Queue

from pyrogram import Client
from pyrogram.types import Message

from agent.main_agent import MainAgent
from db.db_models import BotModel
from db.db_setup import run_init_mongodb_beanie
from db.repository import DBRepository
from logger.logger import logger
from settings import settings


async def message_putting_to_queue_process(
        *,
        bot: BotModel,
        message: Message,
        queue: Queue,
        repo: DBRepository
):
    await bot.set({BotModel.status: "busy"})
    tg_client = Client(
        name=bot.bot_name,
        session_string=bot.tg_user_bot_session
    )

    await queue.put((message, tg_client))
    logger.info(f"Bot started generating response: {tg_client.name}")
    logger.info(f"Message putted to queue: {message}")

    await queue_processing(queue, bot.bot_id, repo=repo)


async def handle_text_message(client: Client, message: Message, repo: DBRepository):
    logger.info(f"Message received from user: User={message.from_user=}, Message={message.text}")
    try:
        await run_init_mongodb_beanie()
        user_ins = await repo.create_user(
            user_id=str(message.from_user.id),
            username=message.from_user.username
        )
        await repo.save_message(
            user_id=user_ins.user_id,
            msg=message,
            role="user",
        )

        agent = MainAgent()
        reply = await agent.generate_response(content=message.text)

        reply = await client.send_message(settings.TG_GROUP_NAME, reply)

        await repo.save_message(
            user_id=user_ins.user_id,
            msg=reply,
            role="agent",
            bot_id=client.me.id,
        )
    except Exception as ex:
        logger.error(f"An error occurred in TG message handler: {ex}")
        raise ex


async def handle_text_message_with_image_reply(client: Client, message: Message, repo: DBRepository):
    logger.info(f"Message received from user: User={message.from_user=}, Message={message.text}")
    try:
        await run_init_mongodb_beanie()
        user_ins = await repo.create_user(
            user_id=str(message.from_user.id),
            username=message.from_user.username
        )
        await repo.save_message(
            user_id=user_ins.user_id,
            msg=message,
            role="user",
        )

        # agent = MainAgent()
        # reply = await agent.generate_response(content=message.text)

        # await message.reply(reply)
        reply = "Photo images.jpg send to the user"
        reply_message = await client.send_photo(
            settings.TG_GROUP_NAME,
            "photos/293578.jpg",
            caption=reply
        )

        await repo.save_message(
            user_id=user_ins.user_id,
            msg=reply_message,
            role="agent",
            bot_id=client.me.id,
            is_image=True
        )
    except Exception as ex:
        logger.error(f"An error occurred in TG message handler: {ex}")
        raise ex


async def queue_processing(queue: Queue, bot_id: int, repo: DBRepository):
    try:
        while True:
            logger.info("Starting queue process")
            message = await queue.get()

            if message is None:
                break

            msg, tg_client = message

            async with tg_client as client:
                await handle_text_message(
                    client=client,
                    message=msg,
                    repo=repo
                ) if client.name.lower().startswith("text") \
                    else await handle_text_message_with_image_reply(
                    client=client,
                    message=msg,
                    repo=repo
                )

                queue.task_done()
                logger.info("Task is done")

                bot = await repo.get_single_bot_from_db(bot_id)
                await bot.set({BotModel.status: "free"})

                logger.info("Bot status set to free")
    except Exception as ex:
        logger.error(f"An error occurred in queue process: {ex}")
        raise ex
    finally:
        bot = await repo.get_single_bot_from_db(bot_id)
        await bot.set({BotModel.status: "free"})


