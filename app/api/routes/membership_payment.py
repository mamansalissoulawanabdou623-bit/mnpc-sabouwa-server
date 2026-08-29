from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from uuid import UUID

from app.db.session import get_db

from app.schemas.membership_payment import (
    MembershipPaymentCreate,
    MembershipPaymentResponse,
    MembershipPaymentValidation,
)

from app.services.membership_payment_service import (
    MembershipPaymentService,
)


router = APIRouter(
    prefix="/membership-payments",
    tags=["Membership Payments"],
)



@router.post(
    "/",
    response_model=MembershipPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_membership_payment(
    data: MembershipPaymentCreate,
    db: Session = Depends(get_db),
):

    service = MembershipPaymentService(db)

    try:

        return service.create_payment(

            member_id=data.member_id,

            amount=data.amount,

            payment_method=data.payment_method,

            transaction_reference=data.transaction_reference,

            receipt_url=data.receipt_url,

        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )





@router.get(
    "/member/{member_id}",
    response_model=list[MembershipPaymentResponse],
)
def get_member_payments(
    member_id: UUID,
    db: Session = Depends(get_db),
):

    service = MembershipPaymentService(db)

    return service.get_member_payments(
        member_id
    )





@router.get(
    "/",
    response_model=list[MembershipPaymentResponse],
)
def get_all_payments(
    db: Session = Depends(get_db),
):

    service = MembershipPaymentService(db)

    return service.list_all_payments()





@router.put(
    "/{payment_id}/validate",
    response_model=MembershipPaymentResponse,
)
def validate_payment(
    payment_id: UUID,
    data: MembershipPaymentValidation,
    user_id: UUID,
    db: Session = Depends(get_db),
):

    service = MembershipPaymentService(db)

    try:

        return service.validate_payment(

            payment_id=payment_id,

            status=data.status,

            user_id=user_id,

        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )