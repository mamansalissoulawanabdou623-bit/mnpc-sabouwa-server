from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.member import Member
from app.models.membership_request import MembershipRequest
from app.models.finance import Finance


class AdminService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    def dashboard(self):

        total_users = self.db.scalar(
            select(func.count(User.id))
        ) or 0


        total_members = self.db.scalar(
            select(func.count(Member.id))
        ) or 0


        pending_requests = self.db.scalar(
            select(func.count(MembershipRequest.id))
            .where(
                MembershipRequest.status == "PENDING"
            )
        ) or 0


        total_finance = self.db.scalar(
            select(func.sum(Finance.amount))
        ) or 0


        return {

            "total_users": total_users,

            "total_members": total_members,

            "pending_membership_requests": pending_requests,

            "total_finance_amount": float(total_finance),

        }


    def list_users(self):

        return list(
            self.db.scalars(
                select(User)
                .order_by(
                    User.created_at.desc()
                )
            ).all()
        )


    def list_members(self):

        return list(
            self.db.scalars(
                select(Member)
                .order_by(
                    Member.created_at.desc()
                )
            ).all()
        )


    def update_user_role(
        self,
        user_id,
        role: str,
    ):

        user = self.db.get(
            User,
            user_id,
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )


        user.role = role.upper()

        self.db.commit()

        self.db.refresh(user)

        return user