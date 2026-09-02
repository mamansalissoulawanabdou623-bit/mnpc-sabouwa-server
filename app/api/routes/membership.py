import uuid

from fastapi import APIRouter, Depends, HTTPException
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

            gender=data.gender,
            birth_date=data.birth_date,
            birth_place=data.birth_place,
            nationality=data.nationality,

            address=data.address,
            region=data.region,
            department=data.department,
            commune=data.commune,
            village_quartier=data.village_quartier,

            profession=data.profession,
            education_level=data.education_level,
            skills_experience=data.skills_experience,

            requested_status=data.requested_status,
            motivation=data.motivation,
            message=data.message,

            photo_url=data.photo_url,

            statutes_accepted=data.statutes_accepted,
            declaration_accepted=data.declaration_accepted,

            card_fee=data.card_fee,
            payment_status=data.payment_status,

            receipt_reference=data.receipt_reference,
            receipt_url=data.receipt_url,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


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
        current_user.id
    )


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


@router.post("/{request_id}/verify-payment")
def verify_membership_payment(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = MembershipService(db)

    try:

        request = service.verify_payment(
            request_id
        )

        return {
            "message": "Paiement verifie.",
            "request_id": str(request.id),
            "payment_status": request.payment_status,
            "payment_verified_at": request.payment_verified_at,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post("/{request_id}/approve")
def approve_membership_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = MembershipService(db)

    try:

        member = service.approve_request(
            request_id
        )

        return {
            "message": "Demande acceptee.",
            "member_id": str(member.id),
            "member_number": member.member_number,
            "status": member.membership_status,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


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
            request_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error