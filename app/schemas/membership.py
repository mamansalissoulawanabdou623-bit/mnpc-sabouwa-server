from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MembershipRequestCreate(BaseModel):

    organization_unit_id: UUID | None = None

    gender: str = Field(
        min_length=1,
        max_length=20,
    )

    birth_date: date

    birth_place: str = Field(
        min_length=1,
        max_length=150,
    )

    nationality: str = Field(
        min_length=1,
        max_length=100,
    )

    address: str = Field(
        min_length=1,
        max_length=255,
    )

    region: str = Field(
        min_length=1,
        max_length=100,
    )

    department: str = Field(
        min_length=1,
        max_length=100,
    )

    commune: str = Field(
        min_length=1,
        max_length=100,
    )

    village_quartier: str = Field(
        min_length=1,
        max_length=150,
    )

    profession: str = Field(
        min_length=1,
        max_length=150,
    )

    education_level: str = Field(
        min_length=1,
        max_length=100,
    )

    skills_experience: str | None = Field(
        default=None,
        max_length=1000,
    )

    requested_status: str = Field(
        min_length=1,
        max_length=100,
    )

    motivation: str = Field(
        min_length=1,
        max_length=1000,
    )

    message: str | None = Field(
        default=None,
        max_length=500,
    )

    photo_url: str | None = Field(
        default=None,
        max_length=500,
    )

    statutes_accepted: bool

    declaration_accepted: bool

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

    gender: str | None

    birth_date: date | None

    birth_place: str | None

    nationality: str | None

    address: str | None

    region: str | None

    department: str | None

    commune: str | None

    village_quartier: str | None

    profession: str | None

    education_level: str | None

    skills_experience: str | None

    requested_status: str | None

    motivation: str | None

    message: str | None

    photo_url: str | None

    statutes_accepted: bool

    declaration_accepted: bool

    card_fee: float

    payment_status: str

    receipt_reference: str | None

    receipt_url: str | None

    payment_verified_at: datetime | None

    card_started_at: datetime | None

    card_expires_at: datetime | None

    created_at: datetime

    updated_at: datetime