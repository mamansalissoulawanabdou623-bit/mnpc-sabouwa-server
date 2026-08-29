from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MembershipRequestCreate(BaseModel):

    organization_unit_id: UUID | None = None

    message: str | None = Field(
        default=None,
        max_length=500,
    )

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    card_fee: float = Field(
        default=2000.0,
        gt=0,
    )

    payment_status: str = Field(
        default="PENDING",
        max_length=30,
    )

    receipt_reference: str | None = Field(
        default=None,
        max_length=100,
    )

    receipt_url: str | None = Field(
        default=None,
        max_length=500,
    )


class MembershipRequestUpdate(BaseModel):

    status: str

    payment_status: str | None = None

    receipt_reference: str | None = None

    receipt_url: str | None = None


class MembershipRequestResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    user_id: UUID

    organization_unit_id: UUID | None

    status: str

    message: str | None

    address: str | None

    card_fee: float

    payment_status: str

    receipt_reference: str | None

    receipt_url: str | None

    payment_verified_at: datetime | None

    card_started_at: datetime | None

    card_expires_at: datetime | None

    created_at: datetime

    updated_at: datetime