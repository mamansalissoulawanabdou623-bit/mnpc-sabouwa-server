import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.organization_responsible import (
    OrganizationResponsibleCreate,
    OrganizationResponsibleResponse,
)
from app.services.organization_responsible_service import (
    OrganizationResponsibleService,
)


router = APIRouter(
    prefix="/organization-responsibles",
    tags=["Responsables des coordinations"],
)


@router.post(
    "/",
    response_model=OrganizationResponsibleResponse,
    status_code=status.HTTP_201_CREATED,
)
def appoint_responsible(
    data: OrganizationResponsibleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = OrganizationResponsibleService(db)

    try:
        return service.appoint_responsible(
            organization_unit_id=data.organization_unit_id,
            member_id=data.member_id,
            appointed_by=admin.id,
            position=data.position,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/",
    response_model=list[OrganizationResponsibleResponse],
)
def list_responsibles(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = OrganizationResponsibleService(db)

    return service.list_responsibles()


@router.get(
    "/{organization_unit_id}",
    response_model=OrganizationResponsibleResponse,
)
def get_responsible_by_unit(
    organization_unit_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = OrganizationResponsibleService(db)

    try:
        return service.get_responsible_by_unit(
            organization_unit_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{responsible_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_responsible(
    responsible_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = OrganizationResponsibleService(db)

    try:
        service.remove_responsible(
            responsible_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error