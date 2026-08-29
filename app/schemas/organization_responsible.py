from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationResponsibleCreate(BaseModel):

    organization_unit_id: UUID

    member_id: UUID

    position: str = Field(
        default="RESPONSABLE",
        min_length=2,
        max_length=100,
    )


class OrganizationResponsibleResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    organization_unit_id: UUID

    member_id: UUID

    appointed_by: UUID

    position: str

    status: str

    appointed_at: datetime

    created_at: datetime

    updated_at: datetime