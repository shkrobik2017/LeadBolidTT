from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from scheduler.scheduler_tasks import send_scheduled_message

scheduler = AsyncIOScheduler()


async def setup_scheduler(client):
    print("Scheduler starting...")
    scheduler.add_job(
        send_scheduled_message,
        trigger=IntervalTrigger(minutes=1),
        id="send_message_job",  # Уникальный ID задачи
        replace_existing=True,  # Перезаписать, если задача с таким ID уже есть
        args=[client]
    )
    scheduler.start()
    print("Scheduler is started")


async def scheduler_stopping():
    scheduler.shutdown()