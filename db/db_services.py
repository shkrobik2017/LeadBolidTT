from typing import Annotated
from uuid import UUID, uuid4

UUIDStr = Annotated[str, lambda v: UUID(v, version=4)]


def get_uuid4_id():
    return str(uuid4())