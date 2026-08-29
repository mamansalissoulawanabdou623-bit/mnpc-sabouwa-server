from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChatGroupBase(BaseModel):
    name: str
    description: str | None = None
    group_type: str = "GENERAL"


class ChatGroupCreate(ChatGroupBase):
    pass


class ChatGroupResponse(ChatGroupBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    members_count: int = 0