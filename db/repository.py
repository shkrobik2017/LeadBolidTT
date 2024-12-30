from typing import List, Type
from beanie.odm.queries.find import FindMany
from db.db_models import MessageModel, ModelType, UserModel
from db.db_services import error_handler
from logger.logger import logger
from redis_app.redis_repository import RedisClient


class DBRepository:
    @staticmethod
    @error_handler
    async def check_object_existing_in_db(
            *,
            model: Type[ModelType],
            filters: dict,
    ) -> ModelType | None:
        if not isinstance(model, MessageModel):
            doc = await model.find(filters).first_or_none()
            return doc
        return None

    @staticmethod
    @error_handler
    async def get_many_objects_from_db(
            *,
            model: Type[ModelType],
            redis: RedisClient
    ) -> List[ModelType]:
        objects_cache = await redis.get_by_key(f"{model}_all_objects")
        if not objects_cache:
            objects = await model.find({}).to_list(length=None)
            serialized_object = [obj.dict() for obj in objects]
            await redis.set_key(key=f"{model}_all_objects", value=serialized_object)
            return objects
        cached_models = [model(**item) for item in objects_cache]
        logger.info(f"Return cached objects: {cached_models}")
        return cached_models

    @staticmethod
    @error_handler
    async def get_chat_history(
            *,
            filters: dict,
            is_for_summarizing: bool = False
    ) -> FindMany[MessageModel] | list[tuple[str, str]]:
        messages = MessageModel.find(filters)
        if is_for_summarizing:
            return messages
        return [
            (item.role, item.content)
            for item in await messages.to_list(length=None)
        ]

    @error_handler
    async def create_object(
            self,
            *,
            model: ModelType,
            filters: dict | None = None,
            redis: RedisClient
    ) -> ModelType | None:
        model_object = await self.check_object_existing_in_db(
            model=type(model),
            filters=filters,
        )
        if model_object is None or isinstance(model, MessageModel):
            new_object = model
            await new_object.create()
            await redis.set_key(
                key=f"{type(new_object)}_{new_object.id}",
                value=new_object.dict()
            )
            logger.info(f"New {model} object created successful")
            return new_object
        logger.info(f"Object {model=}, {filters=} already exist!")
        return model_object

    @error_handler
    async def update_object(
            self,
            *,
            model: ModelType | Type[ModelType],
            filters: dict | None = None,
            redis: RedisClient,
            update_data: dict
    ):
        cached_object = await redis.get_by_key(f"{type(model)}_{model.id}")
        if not cached_object:
            model_object = await self.check_object_existing_in_db(
                model=type(model),
                filters=filters,
            )
            if model_object is not None:
                updated_object = await model_object.set(update_data)
                await redis.set_key(
                    key=f"{type(model)}_{updated_object.id}",
                    value=updated_object.dict()
                )
                return updated_object
            logger.error(f"Object {model=} not found when updating.")
        updated_cached_object = await type(model)(**cached_object).set(update_data)
        await redis.update(
            key=f"{type(updated_cached_object)}_{updated_cached_object.id}",
            value=updated_cached_object.dict()
        )
        return updated_cached_object

    @error_handler
    async def update_messages_status_and_save_summary(
            self,
            user_id: str,
            summary: str,
            redis_client: RedisClient
    ):
        messages = await self.get_chat_history(
            filters={"user_id": user_id, "is_summarized": False},
            is_for_summarizing=True
        )
        for item in await messages.to_list(length=None):
            await item.set({"is_summarized": True})
        logger.info(f"Messages for user {user_id=} summarized successful")

        updated_user = await UserModel.find_one(UserModel.user_id == user_id)
        updated_user.summary = summary
        await updated_user.save()
        await redis_client.update(
            key=f"{type(updated_user)}_{updated_user.id}",
            value=updated_user.dict()
        )
        logger.info(f"User's {user_id=} summary updated successful: {summary=}")


