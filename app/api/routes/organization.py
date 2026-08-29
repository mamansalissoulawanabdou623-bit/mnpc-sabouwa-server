import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.organization import (
    OrganizationUnitCreate,
    OrganizationUnitResponse,
)
from app.services.organization_service import OrganizationService


router = APIRouter(
    prefix="/organization",
    tags=["Organisation"],
)



@router.post(
    "/",
    response_model=OrganizationUnitResponse,
)
def create_organization_unit(
    data: OrganizationUnitCreate,
    db: Session = Depends(get_db),
):

    service = OrganizationService(db)

    try:

        return service.create_unit(
            code=data.code,
            name=data.name,
            unit_type=data.unit_type,
            parent_id=data.parent_id,
            region=data.region,
            department=data.department,
            commune=data.commune,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )



@router.get(
    "/",
    response_model=list[OrganizationUnitResponse],
)
def list_organization_units(
    db: Session = Depends(get_db),
):

    service = OrganizationService(db)

    return service.list_units()



@router.get(
    "/{unit_id}",
    response_model=OrganizationUnitResponse,
)
def get_organization_unit(
    unit_id: uuid.UUID,
    db: Session = Depends(get_db),
):

    service = OrganizationService(db)

    try:

        return service.get_unit(
            unit_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )