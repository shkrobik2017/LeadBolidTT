from beanie import init_beanie
from db.db_data import MONGODB_BEANIE_MODELS_DATA
from db.mongodb_client_creator import MongoDBMotorDBSingletonCreator
from settings import settings

mongodb_motor_client = MongoDBMotorDBSingletonCreator(
    db_name=settings.MONGODB_NAME,
    db_url=settings.MONGODB_URI,
    password=settings.MONGODB_PASSWORD,
    user=settings.MONGODB_USER,
    protocol=settings.MONGODB_PROTOCOL,
    host=settings.MONGODB_HOST,
    port=settings.MONGODB_PORT
).motor_client


async def run_init_mongodb_beanie() -> None:
    await init_beanie(
        database=mongodb_motor_client,
        document_models=list(MONGODB_BEANIE_MODELS_DATA),
    )
