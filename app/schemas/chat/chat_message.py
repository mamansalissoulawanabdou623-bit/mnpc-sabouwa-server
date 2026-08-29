from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChatMessageBase(BaseModel):
    message_type: str = "TEXT"
    message: str | None = None
    media_url: str | None = None
    file_name: str | None = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_id: UUID
    sender_id: UUID
    created_at: datetime
    updated_at: datetime

