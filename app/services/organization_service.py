import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.models.organization_responsible import OrganizationResponsible
from app.models.organization_unit import OrganizationUnit
from app.models.user import User


class OrganizationService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create_unit(
        self,
        *,
        code: str,
        name: str,
        unit_type: str,
        parent_id=None,
        region=None,
        department=None,
        commune=None,
    ):

        existing = self.db.scalar(
            select(OrganizationUnit).where(
                OrganizationUnit.code == code
            )
        )

        if existing:
            raise ValueError(
                "Cette unité existe déjà."
            )

        unit = OrganizationUnit(
            code=code.upper(),
            name=name,
            unit_type=unit_type.upper(),
            parent_id=parent_id,
            region=region,
            department=department,
            commune=commune,
            status="ACTIVE",
        )

        self.db.add(unit)
        self.db.commit()
        self.db.refresh(unit)

        return unit

    def list_units(
        self,
    ):

        return list(
            self.db.scalars(
                select(OrganizationUnit).order_by(
                    OrganizationUnit.name
                )
            ).all()
        )

    def get_unit(
        self,
        unit_id: uuid.UUID,
    ):

        unit = self.db.get(
            OrganizationUnit,
            unit_id,
        )

        if unit is None:
            raise ValueError(
                "Organisation introuvable."
            )

        return unit

    def appoint_responsible(
        self,
        *,
        organization_unit_id: uuid.UUID,
        member_id: uuid.UUID,
        appointed_by: uuid.UUID,
        position: str = "RESPONSABLE",
    ) -> OrganizationResponsible:
        """
        Nomme un membre officiel comme responsable
        d'une coordination.

        Règles :
        - la coordination doit exister ;
        - le membre doit exister ;
        - le membre doit avoir le statut ACTIVE ;
        - l'utilisateur qui nomme doit exister ;
        - une coordination ne peut avoir qu'un seul
          responsable actif ;
        - une ancienne nomination active est remplacée.
        """

        organization_unit = self.db.get(
            OrganizationUnit,
            organization_unit_id,
        )

        if organization_unit is None:
            raise ValueError(
                "Coordination introuvable."
            )

        member = self.db.get(
            Member,
            member_id,
        )

        if member is None:
            raise ValueError(
                "Membre introuvable."
            )

        if member.membership_status != "ACTIVE":
            raise ValueError(
                "Seul un membre officiel ACTIVE peut "
                "être nommé responsable."
            )

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
                "Seule l'administration peut nommer "
                "un responsable."
            )

        existing = self.db.scalar(
            select(OrganizationResponsible).where(
                OrganizationResponsible.organization_unit_id
                == organization_unit_id,
                OrganizationResponsible.status == "ACTIVE",
            )
        )

        if existing is not None:

            if existing.member_id == member_id:
                return existing

            existing.status = "REPLACED"

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

    def get_responsible(
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
                "Aucun responsable n'est actuellement "
                "nommé pour cette coordination."
            )

        return responsible

    def remove_responsible(
        self,
        *,
        organization_unit_id: uuid.UUID,
        appointed_by: uuid.UUID,
    ) -> None:
        """
        Retire le responsable actuel d'une coordination.
        L'action est réservée à l'administration.
        """

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
                "Seule l'administration peut retirer "
                "un responsable."
            )

        responsible = self.db.scalar(
            select(OrganizationResponsible).where(
                OrganizationResponsible.organization_unit_id
                == organization_unit_id,
                OrganizationResponsible.status == "ACTIVE",
            )
        )

        if responsible is None:
            raise ValueError(
                "Aucun responsable actif pour cette coordination."
            )

        responsible.status = "REMOVED"

        self.db.commit()
