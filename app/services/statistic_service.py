from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.models.national_statistic import NationalStatistic


class StatisticService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create_statistic(
        self,
        *,
        statistic_type: str,
        year: int,
        total_members: int = 0,
        total_men: int = 0,
        total_women: int = 0,
        total_youth: int = 0,
        region: str | None = None,
        department: str | None = None,
        commune: str | None = None,
    ) -> NationalStatistic:

        statistic = NationalStatistic(
            statistic_type=statistic_type,
            year=year,
            region=region,
            department=department,
            commune=commune,
            total_members=total_members,
            total_men=total_men,
            total_women=total_women,
            total_youth=total_youth,
        )

        self.db.add(statistic)
        self.db.commit()
        self.db.refresh(statistic)

        return statistic

    def list_statistics(self) -> list[dict]:
        """
        Retourne les statistiques réelles calculées à partir
        des membres enregistrés dans la base de données.

        Aucun enregistrement NationalStatistic n'est nécessaire
        pour afficher les chiffres actuels.
        """

        current_year = datetime.now(timezone.utc).year

        # Membres considérés comme officiellement actifs.
        active_statuses = (
            "ACTIVE",
            "ACTIF",
            "APPROVED",
            "APPROUVÉ",
            "APPROUVE",
            "VALIDATED",
            "VALIDE",
        )

        active_filter = or_(
            Member.membership_status.in_(active_statuses),
            func.upper(Member.membership_status).in_(
                [status.upper() for status in active_statuses]
            ),
        )

        # Total des membres actifs.
        total_members = self.db.scalar(
            select(func.count(Member.id)).where(
                active_filter
            )
        ) or 0

        # Hommes.
        total_men = self.db.scalar(
            select(func.count(Member.id)).where(
                active_filter,
                func.upper(Member.gender).in_(
                    [
                        "M",
                        "MALE",
                        "HOMME",
                        "MASCULIN",
                    ]
                ),
            )
        ) or 0

        # Femmes.
        total_women = self.db.scalar(
            select(func.count(Member.id)).where(
                active_filter,
                func.upper(Member.gender).in_(
                    [
                        "F",
                        "FEMALE",
                        "FEMME",
                        "FEMININ",
                    ]
                ),
            )
        ) or 0

        # Jeunes : 18 à 35 ans inclus.
        today = date.today()

        youth_min_birth_date = date(
            today.year - 35,
            today.month,
            today.day,
        )

        youth_max_birth_date = date(
            today.year - 18,
            today.month,
            today.day,
        )

        total_youth = self.db.scalar(
            select(func.count(Member.id)).where(
                active_filter,
                Member.birth_date.is_not(None),
                Member.birth_date >= youth_min_birth_date,
                Member.birth_date <= youth_max_birth_date,
            )
        ) or 0

        return [
            {
                "id": uuid4(),
                "statistic_type": "Membres actuels",
                "year": current_year,
                "region": None,
                "department": None,
                "commune": None,
                "total_members": int(total_members),
                "total_men": int(total_men),
                "total_women": int(total_women),
                "total_youth": int(total_youth),
                "created_at": datetime.now(timezone.utc),
            }
        ]
