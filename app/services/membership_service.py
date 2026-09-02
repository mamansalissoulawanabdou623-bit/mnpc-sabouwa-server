from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.models.membership_request import MembershipRequest
from app.models.user import User


class MembershipService:
    CARD_FEE = 2000.0
    CARD_VALIDITY_YEARS = 2

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # OUTILS
    # ==========================================================

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _add_years(value: datetime, years: int) -> datetime:
        """
        Ajoute un nombre d'années sans problème particulier
        pour le 29 février.
        """
        try:
            return value.replace(year=value.year + years)
        except ValueError:
            return value.replace(
                year=value.year + years,
                day=28,
            )

    def _generate_member_number(self) -> str:
        """
        Génère un numéro de membre unique.
        Exemple : MNPC-A1B2C3D4
        """
        while True:
            number = f"MNPC-{uuid4().hex[:8].upper()}"

            existing = self.db.scalar(
                select(Member).where(
                    Member.member_number == number
                )
            )

            if existing is None:
                return number

    # ==========================================================
    # CREATION D'UNE DEMANDE
    # ==========================================================

    def create_request(
        self,
        user_id: UUID,
        data,
    ) -> MembershipRequest:
        user = self.db.get(User, user_id)

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        # L'utilisateur est déjà membre
        if getattr(user, "member_id", None) is not None:
            raise ValueError(
                "Cet utilisateur est déjà membre."
            )

        existing_member = self.db.scalar(
            select(Member).where(
                Member.user_id == user_id
            )
        )

        if existing_member is not None:
            raise ValueError(
                "Cet utilisateur est déjà membre."
            )

        # Une demande PENDING existe déjà
        existing_request = self.db.scalar(
            select(MembershipRequest)
            .where(
                MembershipRequest.user_id == user_id,
                MembershipRequest.status == "PENDING",
            )
            .order_by(
                MembershipRequest.created_at.desc()
            )
        )

        if existing_request is not None:
            return existing_request

        # Vérification de la cotisation
        card_fee = float(
            getattr(
                data,
                "card_fee",
                self.CARD_FEE,
            )
        )

        if card_fee != self.CARD_FEE:
            raise ValueError(
                "La cotisation d'adhésion est de 2 000 F CFA."
            )

        # Acceptation des statuts
        if not bool(
            getattr(
                data,
                "statutes_accepted",
                False,
            )
        ):
            raise ValueError(
                "Vous devez accepter les statuts du MNPC-SABOUWA."
            )

        # Déclaration
        if not bool(
            getattr(
                data,
                "declaration_accepted",
                False,
            )
        ):
            raise ValueError(
                "Vous devez confirmer l'exactitude "
                "des informations fournies."
            )

        payment_status = str(
            getattr(
                data,
                "payment_status",
                "PENDING",
            )
        ).upper()

        allowed_payment_statuses = {
            "PENDING",
            "PAID",
            "REJECTED",
        }

        if payment_status not in allowed_payment_statuses:
            raise ValueError(
                "Statut de paiement invalide."
            )

        request = MembershipRequest(
            user_id=user_id,

            organization_unit_id=getattr(
                data,
                "organization_unit_id",
                None,
            ),

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
            skills_experience=getattr(
                data,
                "skills_experience",
                None,
            ),

            requested_status=data.requested_status,
            motivation=data.motivation,

            message=getattr(
                data,
                "message",
                None,
            ),

            photo_url=getattr(
                data,
                "photo_url",
                None,
            ),

            statutes_accepted=True,
            declaration_accepted=True,

            status="PENDING",

            card_fee=self.CARD_FEE,

            payment_status=payment_status,

            receipt_reference=getattr(
                data,
                "receipt_reference",
                None,
            ),

            receipt_url=getattr(
                data,
                "receipt_url",
                None,
            ),
        )

        try:
            self.db.add(request)
            self.db.commit()
            self.db.refresh(request)

            return request

        except Exception:
            self.db.rollback()
            raise

    # ==========================================================
    # MES DEMANDES
    # ==========================================================

    def get_my_requests(
        self,
        user_id: UUID,
    ) -> list[MembershipRequest]:

        result = self.db.scalars(
            select(MembershipRequest)
            .where(
                MembershipRequest.user_id == user_id
            )
            .order_by(
                MembershipRequest.created_at.desc()
            )
        )

        return list(result.all())

    # ==========================================================
    # TOUTES LES DEMANDES
    # ==========================================================

    def list_requests(self) -> list[MembershipRequest]:

        result = self.db.scalars(
            select(MembershipRequest)
            .order_by(
                MembershipRequest.created_at.desc()
            )
        )

        return list(result.all())

    # ==========================================================
    # TROUVER UNE DEMANDE
    # ==========================================================

    def get_request(
        self,
        request_id: UUID,
    ) -> MembershipRequest:

        request = self.db.get(
            MembershipRequest,
            request_id,
        )

        if request is None:
            raise ValueError(
                "Demande d'adhésion introuvable."
            )

        return request

    # ==========================================================
    # VERIFICATION DU PAIEMENT
    # ==========================================================

    def verify_payment(
        self,
        request_id: UUID,
    ) -> MembershipRequest:

        request = self.get_request(request_id)

        receipt_reference = (
            request.receipt_reference
        )

        receipt_url = request.receipt_url

        if (
            not receipt_reference
            and not receipt_url
        ):
            raise ValueError(
                "Un justificatif de paiement "
                "est nécessaire avant la vérification."
            )

        request.payment_status = "PAID"
        request.payment_verified_at = self._now()

        try:
            self.db.commit()
            self.db.refresh(request)

            return request

        except Exception:
            self.db.rollback()
            raise

    # ==========================================================
    # APPROUVER UNE DEMANDE
    # ==========================================================

    def approve(
        self,
        request_id: UUID,
    ) -> MembershipRequest:

        request = self.get_request(request_id)

        # Déjà approuvée
        if request.status == "APPROVED":
            return request

        # Paiement obligatoire
        if request.payment_status != "PAID":
            raise ValueError(
                "Le paiement de 2 000 F CFA doit être "
                "vérifié avant l'approbation."
            )

        user = self.db.get(
            User,
            request.user_id,
        )

        if user is None:
            raise ValueError(
                "Utilisateur associé à la demande introuvable."
            )

        # Vérifier si le membre existe déjà
        existing_member = self.db.scalar(
            select(Member).where(
                Member.user_id == request.user_id
            )
        )

        if existing_member is not None:
            raise ValueError(
                "Cet utilisateur possède déjà un compte membre."
            )

        now = self._now()

        member = Member(
            user_id=request.user_id,
            member_number=self._generate_member_number(),
            birth_date=request.birth_date,
            gender=request.gender,
            profession=request.profession,
            status="ACTIVE",
            joined_at=now,
        )

        try:
            # Ajouter le membre
            self.db.add(member)

            # Obtenir son UUID avant de mettre à jour User
            self.db.flush()

            # Lier User au membre
            user.member_id = member.id
            user.account_status = "ACTIVE"

            # Mettre à jour la demande
            request.status = "APPROVED"

            # Carte membre
            request.card_started_at = now
            request.card_expires_at = self._add_years(
                now,
                self.CARD_VALIDITY_YEARS,
            )

            self.db.commit()
            self.db.refresh(request)

            return request

        except Exception:
            self.db.rollback()
            raise

    # ==========================================================
    # REJETER UNE DEMANDE
    # ==========================================================

    def reject(
        self,
        request_id: UUID,
    ) -> MembershipRequest:

        request = self.get_request(request_id)

        if request.status == "APPROVED":
            raise ValueError(
                "Une demande déjà approuvée ne peut pas être rejetée."
            )

        request.status = "REJECTED"

        if request.payment_status == "PAID":
            request.payment_status = "REJECTED"

        try:
            self.db.commit()
            self.db.refresh(request)

            return request

        except Exception:
            self.db.rollback()
            raise