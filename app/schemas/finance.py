from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FinanceCreate(BaseModel):

    member_id: UUID | None = None

    transaction_type: str = Field(
        min_length=2,
        max_length=50,
    )

    amount: float = Field(
        gt=0,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )



class FinanceResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    member_id: UUID | None

    transaction_type: str

    amount: float

    description: str | None

    status: str

    created_at: datetime



class FinanceBalanceResponse(BaseModel):

    total_income: float

    total_expense: float

    balance: float