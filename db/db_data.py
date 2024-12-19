from beanie import Document

from db.db_models import UserModel, BotModel, MessageModel

MONGODB_BEANIE_MODELS_DATA: frozenset[type[Document]] = frozenset(
    {
        UserModel,
        BotModel,
        MessageModel
    },
)