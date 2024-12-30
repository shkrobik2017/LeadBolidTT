from typing import Union
from beanie import Document
from datetime import datetime
from pydantic import BaseModel, Field
from db.db_services import get_uuid4_id, UUIDStr


class CommonModel(BaseModel):
    id: UUIDStr = Field(default_factory=get_uuid4_id, alias="_id")
    created_at: str = Field(default=str(datetime.now()))


class BaseDocument(CommonModel, Document):
    pass


class UserModel(BaseDocument):
    user_id: str
    username: str
    summary: str = Field(default="")


class MessageModel(BaseDocument):
    user_id: str
    content: str
    role: str
    message_id: int
    bot_id: int | None = Field(default=None)
    is_summarized: bool = Field(default=False)


class BotModel(BaseDocument):
    tg_user_bot_session: str
    bot_name: str
    bot_id: int
    status: str = Field(default="free")
    is_in_worker: bool = Field(default=False)


class GroupModel(BaseDocument):
    group_name: str
    group_prompt_name: str


ModelType = Union[UserModel, MessageModel, BotModel, GroupModel]
