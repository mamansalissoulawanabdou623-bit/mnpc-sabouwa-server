import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.models.user import User


class MemberService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create_member(
        self,
        *,
        user_id: uuid.UUID,
        member_number: str | None = None,
        organization_unit_id: uuid.UUID | None = None,
        birth_date=None,
        gender: str | None = None,
        profession: str | None = None,
    ) -> Member:

        user = self.db.get(
            User,
            user_id,
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        existing = self.db.scalar(
            select(Member).where(
                Member.user_id == user_id
            )
        )

        if existing is not None:
            return existing

        if not member_number:
            member_number = self.generate_member_number()

        member = Member(
            user_id=user_id,
            organization_unit_id=organization_unit_id,
            member_number=member_number.upper(),
            birth_date=birth_date,
            gender=gender,
            profession=profession,
            membership_status="PENDING",
        )

        self.db.add(member)
        self.db.flush()

        user.member_id = member.id

        self.db.commit()
        self.db.refresh(member)

        return member

    def generate_member_number(self) -> str:
        """
        Génère un numéro membre unique.
        Exemple : MNPC-8A42F1C9
        """

        while True:
            number = (
                "MNPC-"
                + uuid.uuid4().hex[:8].upper()
            )

            existing = self.db.scalar(
                select(Member).where(
                    Member.member_number == number
                )
            )

            if existing is None:
                return number

    def get_member(
        self,
        member_id: uuid.UUID,
    ) -> Member:

        member = self.db.get(
            Member,
            member_id,
        )

        if member is None:
            raise ValueError(
                "Membre introuvable."
            )

        return member

    def get_member_by_user(
        self,
        user_id: uuid.UUID,
    ) -> Member:

        member = self.db.scalar(
            select(Member).where(
                Member.user_id == user_id
            )
        )

        if member is None:
            raise ValueError(
                "Profil membre introuvable."
            )

        return member

    def list_members(
        self,
    ) -> list[Member]:

        return list(
            self.db.scalars(
                select(Member)
                .order_by(
                    Member.created_at.desc()
                )
            ).all()
        )

    def approve_member(
        self,
        member_id: uuid.UUID,
    ) -> Member:

        member = self.get_member(
            member_id
        )

        member.membership_status = "ACTIVE"

        member.joined_at = datetime.now(
            timezone.utc
        )

        self.db.commit()
        self.db.refresh(member)

        return member