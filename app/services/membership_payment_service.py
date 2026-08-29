from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.membership_payment import MembershipPayment


class MembershipPaymentService:


    def __init__(self, db: Session):
        self.db = db



    def create_payment(
        self,
        member_id: UUID,
        amount: float,
        payment_method: str,
        transaction_reference: str | None = None,
        receipt_url: str | None = None,
    ):

        payment = MembershipPayment(

            member_id=member_id,

            amount=amount,

            payment_method=payment_method,

            transaction_reference=transaction_reference,

            receipt_url=receipt_url,

            payment_status="PENDING",

        )


        self.db.add(payment)

        self.db.commit()

        self.db.refresh(payment)


        return payment




    def get_member_payments(
        self,
        member_id: UUID,
    ):

        return (
            self.db.query(MembershipPayment)
            .filter(
                MembershipPayment.member_id == member_id
            )
            .order_by(
                MembershipPayment.created_at.desc()
            )
            .all()
        )




    def list_all_payments(self):

        return (
            self.db.query(MembershipPayment)
            .order_by(
                MembershipPayment.created_at.desc()
            )
            .all()
        )




    def validate_payment(
        self,
        payment_id: UUID,
        status: str,
        user_id: UUID,
    ):

        payment = (
            self.db.query(MembershipPayment)
            .filter(
                MembershipPayment.id == payment_id
            )
            .first()
        )


        if not payment:
            raise ValueError(
                "Paiement introuvable"
            )


        payment.payment_status = status

        payment.verified_by = user_id

        payment.verified_at = datetime.now(
            timezone.utc
        )


        self.db.commit()

        self.db.refresh(payment)


        return payment