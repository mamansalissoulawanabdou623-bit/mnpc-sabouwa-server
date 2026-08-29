from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationUnitCreate(BaseModel):

    code: str = Field(
        min_length=2,
        max_length=50,
    )

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    unit_type: str = Field(
        min_length=2,
        max_length=50,
    )

    parent_id: UUID | None = None

    region: str | None = None

    department: str | None = None

    commune: str | None = None


class OrganizationUnitUpdate(BaseModel):

    name: str | None = None

    status: str | None = None


class OrganizationUnitResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    parent_id: UUID | None

    code: str

    name: str

    unit_type: str

    region: str | None

    department: str | None

    commune: str | None

    status: str

    created_at: datetime

    updated_at: datetime