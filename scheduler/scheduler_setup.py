from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from logger.logger import logger
from scheduler.scheduler_tasks import send_scheduled_message, agents_conversation_job
from settings import settings

scheduler = AsyncIOScheduler()


async def setup_scheduler(client, repo, redis_client):
    logger.info("Scheduler starting...")
    scheduler.add_job(
        send_scheduled_message,
        trigger=IntervalTrigger(minutes=settings.SENDING_MEDIA_SCHEDULE),
        id="send_message_job",
        replace_existing=True,
        args=[client]
    )
    scheduler.add_job(
        func=agents_conversation_job,
        trigger=IntervalTrigger(minutes=settings.AGENTS_CONVERSATION_SCHEDULE),
        id="agents_conversation",
        replace_existing=True,
        args=[repo, redis_client]
    )
    scheduler.start()


async def scheduler_stopping():
    scheduler.shutdown()
