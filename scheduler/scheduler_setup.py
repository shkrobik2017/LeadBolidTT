from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from logger.logger import logger
from scheduler.scheduler_data_to_send import SCHEDULER_DATA_TO_SEND
from scheduler.scheduler_tasks import send_scheduled_message

scheduler = AsyncIOScheduler()


async def setup_scheduler(client):
    logger.info("Scheduler starting...")
    scheduler.add_job(
        send_scheduled_message,
        trigger=IntervalTrigger(hours=10),
        id="send_message_job",
        replace_existing=True,
        args=[client, SCHEDULER_DATA_TO_SEND]
    )
    scheduler.start()
    logger.info("Scheduler is started")


async def scheduler_stopping():
    scheduler.shutdown()
    logger.info("Scheduler is stopped")
