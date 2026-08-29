from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NationalStatisticCreate(BaseModel):

    statistic_type: str = Field(
        min_length=2,
        max_length=50,
    )

    year: int

    region: str | None = None

    department: str | None = None

    commune: str | None = None

    total_members: int = 0

    total_men: int = 0

    total_women: int = 0

    total_youth: int = 0



class NationalStatisticResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    statistic_type: str

    year: int

    region: str | None

    department: str | None

    commune: str | None

    total_members: int

    total_men: int

    total_women: int

    total_youth: int

    created_at: datetime