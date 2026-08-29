from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MemberCreate(BaseModel):

    user_id: UUID

    organization_unit_id: UUID | None = None

    member_number: str = Field(
        min_length=3,
        max_length=50,
    )

    birth_date: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=20,
    )

    profession: str | None = Field(
        default=None,
        max_length=150,
    )


class MemberUpdate(BaseModel):

    organization_unit_id: UUID | None = None

    birth_date: date | None = None

    gender: str | None = None

    profession: str | None = None

    membership_status: str | None = None


class MemberResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    user_id: UUID

    organization_unit_id: UUID | None

    member_number: str

    birth_date: date | None

    gender: str | None

    profession: str | None

    membership_status: str

    joined_at: datetime | None

    created_at: datetime

    updated_at: datetime