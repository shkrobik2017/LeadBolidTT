from beanie import Document
from datetime import datetime
from pydantic import BaseModel, Field

from db.db_services import get_uuid4_id, UUIDStr


class CommonModel(BaseModel):
    id: UUIDStr = Field(default_factory=get_uuid4_id, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)


class UserModel(CommonModel, Document):
    user_id: UUIDStr
    username: str


class MessageModel(CommonModel, Document):
    chat_id: UUIDStr
    content: str
    role: str


class BotModel(CommonModel, Document):
    tg_user_bot_session: str
    bot_name: str
    bot_id: int
    status: str = Field(default="free")
