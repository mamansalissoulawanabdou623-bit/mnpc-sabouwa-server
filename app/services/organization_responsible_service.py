import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.models.organization_responsible import OrganizationResponsible
from app.models.organization_unit import OrganizationUnit
from app.models.user import User


class OrganizationResponsibleService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def appoint_responsible(
        self,
        *,
        organization_unit_id: uuid.UUID,
        member_id: uuid.UUID,
        appointed_by: uuid.UUID,
        position: str = "RESPONSABLE",
    ) -> OrganizationResponsible:

        # Vérifier la coordination
        organization_unit = self.db.get(
            OrganizationUnit,
            organization_unit_id,
        )

        if organization_unit is None:
            raise ValueError(
                "Coordination introuvable."
            )

        # Vérifier le membre
        member = self.db.get(
            Member,
            member_id,
        )

        if member is None:
            raise ValueError(
                "Membre introuvable."
            )

        # Seuls les membres officiels peuvent devenir responsables
        if member.membership_status.upper() != "ACTIVE":
            raise ValueError(
                "Seul un membre officiel peut être nommé responsable."
            )

        # Vérifier l'utilisateur qui nomme
        administrator = self.db.get(
            User,
            appointed_by,
        )

        if administrator is None:
            raise ValueError(
                "Administrateur introuvable."
            )

        if administrator.role.upper() != "ADMIN":
            raise ValueError(
                "Seule l'administration peut nommer un responsable."
            )

        # Une coordination ne peut avoir qu'un responsable actif
        existing = self.db.scalar(
            select(OrganizationResponsible).where(
                OrganizationResponsible.organization_unit_id
                == organization_unit_id
            )
        )

        if existing is not None:
            raise ValueError(
                "Cette coordination possède déjà un responsable."
            )

        # Un même membre ne peut pas être responsable de plusieurs
        # coordinations avec cette affectation.
        existing_member = self.db.scalar(
            select(OrganizationResponsible).where(
                OrganizationResponsible.member_id
                == member_id
            )
        )

        if existing_member is not None:
            raise ValueError(
                "Ce membre est déjà responsable d'une coordination."
            )

        responsible = OrganizationResponsible(
            organization_unit_id=organization_unit_id,
            member_id=member_id,
            appointed_by=appointed_by,
            position=position.upper(),
            status="ACTIVE",
            appointed_at=datetime.now(timezone.utc),
        )

        self.db.add(responsible)
        self.db.commit()
        self.db.refresh(responsible)

        return responsible

    def list_responsibles(
        self,
    ) -> list[OrganizationResponsible]:

        return list(
            self.db.scalars(
                select(OrganizationResponsible)
                .where(
                    OrganizationResponsible.status == "ACTIVE"
                )
                .order_by(
                    OrganizationResponsible.created_at.desc()
                )
            ).all()
        )

    def get_responsible(
        self,
        responsible_id: uuid.UUID,
    ) -> OrganizationResponsible:

        responsible = self.db.get(
            OrganizationResponsible,
            responsible_id,
        )

        if responsible is None:
            raise ValueError(
                "Responsable introuvable."
            )

        return responsible

    def get_responsible_by_unit(
        self,
        organization_unit_id: uuid.UUID,
    ) -> OrganizationResponsible:

        responsible = self.db.scalar(
            select(OrganizationResponsible).where(
                OrganizationResponsible.organization_unit_id
                == organization_unit_id,
                OrganizationResponsible.status == "ACTIVE",
            )
        )

        if responsible is None:
            raise ValueError(
                "Aucun responsable n'est nommé pour cette coordination."
            )

        return responsible

    def remove_responsible(
        self,
        responsible_id: uuid.UUID,
    ) -> None:

        responsible = self.get_responsible(
            responsible_id
        )

        responsible.status = "INACTIVE"

        self.db.commit()