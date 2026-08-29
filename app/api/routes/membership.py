import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.membership import (
    MembershipRequestCreate,
    MembershipRequestResponse,
)
from app.services.membership_service import MembershipService


router = APIRouter(
    prefix="/membership",
    tags=["Adhesion"],
)


# ==========================================================
# CREER MA DEMANDE D'ADHESION
# UTILISATEUR CONNECTE
# ==========================================================

@router.post(
    "/",
    response_model=MembershipRequestResponse,
)
def create_membership_request(
    data: MembershipRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MembershipService(db)

    try:
        return service.create_request(
            user_id=current_user.id,
            organization_unit_id=data.organization_unit_id,
            message=data.message,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


# ==========================================================
# MES DEMANDES D'ADHESION
# UTILISATEUR CONNECTE
# ==========================================================

@router.get(
    "/mine",
    response_model=list[MembershipRequestResponse],
)
def list_my_membership_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MembershipService(db)

    return service.list_user_requests(
        current_user.id,
    )


# ==========================================================
# LISTE DE TOUTES LES DEMANDES
# ADMIN UNIQUEMENT
# ==========================================================

@router.get(
    "/",
    response_model=list[MembershipRequestResponse],
)
def list_membership_requests(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = MembershipService(db)

    return service.list_requests()


# ==========================================================
# APPROUVER UNE DEMANDE
# ADMIN UNIQUEMENT
# ==========================================================

@router.post(
    "/{request_id}/approve",
)
def approve_membership_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = MembershipService(db)

    try:
        member = service.approve_request(
            request_id,
        )

        return {
            "message": "Demande acceptee.",
            "member_id": str(member.id),
            "member_number": member.member_number,
            "status": member.membership_status,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


# ==========================================================
# REFUSER UNE DEMANDE
# ADMIN UNIQUEMENT
# ==========================================================

@router.post(
    "/{request_id}/reject",
    response_model=MembershipRequestResponse,
)
def reject_membership_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = MembershipService(db)

    try:
        return service.reject_request(
            request_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error