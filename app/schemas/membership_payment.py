from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MembershipPaymentCreate(BaseModel):

    member_id: UUID

    amount: float = Field(
        default=2000.0,
        gt=0,
    )

    payment_method: str = Field(
        min_length=2,
        max_length=50,
    )

    transaction_reference: str | None = Field(
        default=None,
        max_length=100,
    )

    receipt_url: str | None = Field(
        default=None,
        max_length=500,
    )



class MembershipPaymentResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    member_id: UUID

    amount: float

    payment_method: str

    transaction_reference: str | None

    receipt_url: str | None

    payment_status: str

    verified_by: UUID | None

    created_at: datetime

    verified_at: datetime | None



class MembershipPaymentValidation(BaseModel):

    status: str = Field(
        pattern="^(VERIFIED|REJECTED)$"
    )