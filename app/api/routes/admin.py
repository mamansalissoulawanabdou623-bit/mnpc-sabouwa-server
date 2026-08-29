from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.organization_responsible import OrganizationResponsible
from app.models.user import User
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminMemberResponse,
    AdminUserResponse,
    UpdateRoleRequest,
)
from app.services.admin_service import AdminService
from app.services.organization_service import OrganizationService


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


class AppointResponsibleRequest(BaseModel):
    """
    Données envoyées par l'administration pour
    nommer un responsable de coordination.
    """

    member_id: UUID

    position: str = Field(
        default="RESPONSABLE",
        min_length=2,
        max_length=100,
    )


class OrganizationResponsibleResponse(BaseModel):
    """
    Réponse après nomination d'un responsable.
    """

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


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
)
def dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = AdminService(db)

    return service.dashboard()


@router.get(
    "/users",
    response_model=list[AdminUserResponse],
)
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = AdminService(db)

    return service.list_users()


@router.get(
    "/members",
    response_model=list[AdminMemberResponse],
)
def list_members(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = AdminService(db)

    return service.list_members()


@router.patch(
    "/users/{user_id}/role",
    response_model=AdminUserResponse,
)
def update_role(
    user_id: UUID,
    data: UpdateRoleRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = AdminService(db)

    try:

        return service.update_user_role(
            user_id,
            data.role,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/organization/{organization_unit_id}/responsible",
    response_model=OrganizationResponsibleResponse,
    status_code=status.HTTP_201_CREATED,
)
def appoint_organization_responsible(
    organization_unit_id: UUID,
    data: AppointResponsibleRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = OrganizationService(db)

    try:

        return service.appoint_responsible(
            organization_unit_id=organization_unit_id,
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
    "/organization/{organization_unit_id}/responsible",
    response_model=OrganizationResponsibleResponse,
)
def get_organization_responsible(
    organization_unit_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = OrganizationService(db)

    try:

        return service.get_responsible(
            organization_unit_id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/organization/{organization_unit_id}/responsible",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_organization_responsible(
    organization_unit_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = OrganizationService(db)

    try:

        service.remove_responsible(
            organization_unit_id=organization_unit_id,
            appointed_by=admin.id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return None
