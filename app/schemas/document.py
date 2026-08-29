from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):

    title: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    document_type: str = Field(
        default="GENERAL",
        min_length=2,
        max_length=50,
    )

    file_url: str = Field(
        min_length=1,
        max_length=500,
    )


class DocumentUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    document_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    file_url: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )


class DocumentResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    title: str

    description: str | None

    document_type: str

    file_url: str

    created_by: UUID | None

    created_at: datetime

    updated_at: datetime
