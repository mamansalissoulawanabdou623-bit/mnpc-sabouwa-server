import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.models.membership_request import MembershipRequest
from app.models.user import User


class MembershipService:

    CARD_FEE = 2000.0
    CARD_VALIDITY_YEARS = 2

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    # ==========================================================
    # CREER UNE DEMANDE D'ADHESION
    # ==========================================================

    def create_request(
        self,
        *,
        user_id: uuid.UUID,
        organization_unit_id: uuid.UUID | None = None,
        message: str | None = None,
        address: str | None = None,
        card_fee: float = CARD_FEE,
        payment_status: str = "PENDING",
        receipt_reference: str | None = None,
        receipt_url: str | None = None,
    ) -> MembershipRequest:

        # ------------------------------------------------------
        # Vérifier que l'utilisateur existe
        # ------------------------------------------------------

        user = self.db.get(
            User,
            user_id,
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        # ------------------------------------------------------
        # Vérifier si l'utilisateur est déjà membre
        # ------------------------------------------------------

        existing_member = self.db.scalar(
            select(Member).where(
                Member.user_id == user_id
            )
        )

        if existing_member is not None:
            raise ValueError(
                "Cet utilisateur est deja membre."
            )

        # ------------------------------------------------------
        # Vérifier s'il existe déjà une demande en attente
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # Nettoyer le message
        # ------------------------------------------------------

        cleaned_message = None

        if message is not None:
            cleaned_message = message.strip()

            if cleaned_message == "":
                cleaned_message = None

        # ------------------------------------------------------
        # Nettoyer l'adresse
        # ------------------------------------------------------

        cleaned_address = None

        if address is not None:
            cleaned_address = address.strip()

            if cleaned_address == "":
                cleaned_address = None

        # ------------------------------------------------------
        # Vérifier les frais de carte
        # ------------------------------------------------------

        if card_fee != self.CARD_FEE:
            raise ValueError(
                "Les frais de la carte de membre sont fixes à 2 000 F CFA."
            )

        # ------------------------------------------------------
        # Normaliser le statut du paiement
        # ------------------------------------------------------

        normalized_payment_status = (
            payment_status.upper().strip()
            if payment_status
            else "PENDING"
        )

        allowed_payment_statuses = {
            "PENDING",
            "PAID",
            "REJECTED",
        }

        if normalized_payment_status not in allowed_payment_statuses:
            raise ValueError(
                "Statut de paiement invalide."
            )

        # ------------------------------------------------------
        # Une preuve de paiement doit avoir une référence
        # ou une adresse de fichier.
        # ------------------------------------------------------

        cleaned_receipt_reference = None

        if receipt_reference is not None:
            cleaned_receipt_reference = receipt_reference.strip()

            if cleaned_receipt_reference == "":
                cleaned_receipt_reference = None

        cleaned_receipt_url = None

        if receipt_url is not None:
            cleaned_receipt_url = receipt_url.strip()

            if cleaned_receipt_url == "":
                cleaned_receipt_url = None

        # ------------------------------------------------------
        # Créer la demande
        # ------------------------------------------------------

        request = MembershipRequest(
            user_id=user_id,
            organization_unit_id=organization_unit_id,
            message=cleaned_message,
            address=cleaned_address,
            card_fee=self.CARD_FEE,
            payment_status=normalized_payment_status,
            receipt_reference=cleaned_receipt_reference,
            receipt_url=cleaned_receipt_url,
            status="PENDING",
        )

        self.db.add(request)

        self.db.commit()

        self.db.refresh(request)

        return request

    # ==========================================================
    # LISTE DE TOUTES LES DEMANDES
    # ADMINISTRATION
    # ==========================================================

    def list_requests(
        self,
    ) -> list[MembershipRequest]:

        requests = self.db.scalars(
            select(MembershipRequest)
            .order_by(
                MembershipRequest.created_at.desc()
            )
        ).all()

        return list(requests)

    # ==========================================================
    # LISTE DES DEMANDES D'UN UTILISATEUR
    # ==========================================================

    def list_user_requests(
        self,
        user_id: uuid.UUID,
    ) -> list[MembershipRequest]:

        requests = self.db.scalars(
            select(MembershipRequest)
            .where(
                MembershipRequest.user_id == user_id
            )
            .order_by(
                MembershipRequest.created_at.desc()
            )
        ).all()

        return list(requests)

    # ==========================================================
    # VERIFIER LE PAIEMENT
    # ADMINISTRATION
    # ==========================================================

    def verify_payment(
        self,
        request_id: uuid.UUID,
    ) -> MembershipRequest:

        request = self.db.get(
            MembershipRequest,
            request_id,
        )

        if request is None:
            raise ValueError(
                "Demande introuvable."
            )

        if request.status == "REJECTED":
            raise ValueError(
                "Cette demande a deja ete rejetee."
            )

        if request.status == "APPROVED":
            raise ValueError(
                "Cette demande a deja ete approuvee."
            )

        if request.card_fee != self.CARD_FEE:
            raise ValueError(
                "Le montant de la carte doit etre de 2 000 F CFA."
            )

        if (
            request.receipt_reference is None
            and request.receipt_url is None
        ):
            raise ValueError(
                "Aucun recu ou preuve de paiement n'est fourni."
            )

        request.payment_status = "PAID"

        request.payment_verified_at = datetime.now(
            timezone.utc
        )

        self.db.commit()

        self.db.refresh(request)

        return request

    # ==========================================================
    # APPROUVER UNE DEMANDE
    # ADMINISTRATION
    #
    # IMPORTANT :
    # Le paiement doit être vérifié avant l'approbation.
    # ==========================================================

    def approve_request(
        self,
        request_id: uuid.UUID,
    ) -> Member:

        request = self.db.get(
            MembershipRequest,
            request_id,
        )

        if request is None:
            raise ValueError(
                "Demande introuvable."
            )

        # ------------------------------------------------------
        # Vérifier si le membre existe déjà
        # ------------------------------------------------------

        existing_member = self.db.scalar(
            select(Member).where(
                Member.user_id == request.user_id
            )
        )

        if existing_member is not None:

            if request.status != "APPROVED":
                request.status = "APPROVED"

                self.db.commit()

                self.db.refresh(
                    existing_member
                )

            return existing_member

        # ------------------------------------------------------
        # Une demande rejetée ne peut pas être approuvée
        # ------------------------------------------------------

        if request.status == "REJECTED":
            raise ValueError(
                "Cette demande a deja ete rejetee."
            )

        # ------------------------------------------------------
        # Le paiement doit être vérifié
        # ------------------------------------------------------

        if request.payment_status != "PAID":
            raise ValueError(
                "Le paiement de 2 000 F CFA doit etre verifie "
                "avant de valider la demande."
            )

        # ------------------------------------------------------
        # Vérifier l'utilisateur
        # ------------------------------------------------------

        user = self.db.get(
            User,
            request.user_id,
        )

        if user is None:
            raise ValueError(
                "Utilisateur associe a la demande introuvable."
            )

        # ------------------------------------------------------
        # Dates de validité de la carte
        # ------------------------------------------------------

        now = datetime.now(
            timezone.utc
        )

        expires_at = now + timedelta(
            days=365 * self.CARD_VALIDITY_YEARS
        )

        # ------------------------------------------------------
        # Approuver la demande
        # ------------------------------------------------------

        request.status = "APPROVED"

        request.card_started_at = now

        request.card_expires_at = expires_at

        # ------------------------------------------------------
        # Créer automatiquement le membre
        # ------------------------------------------------------

        member = Member(
            user_id=request.user_id,
            organization_unit_id=request.organization_unit_id,
            member_number=self.generate_member_number(),
            membership_status="ACTIVE",
            joined_at=now,
        )

        self.db.add(member)

        # ------------------------------------------------------
        # Générer l'identifiant du membre
        # ------------------------------------------------------

        self.db.flush()

        # ------------------------------------------------------
        # Mettre à jour le compte utilisateur
        # ------------------------------------------------------

        user.member_id = member.id

        user.account_status = "ACTIVE"

        # ------------------------------------------------------
        # Enregistrer définitivement
        # ------------------------------------------------------

        self.db.commit()

        self.db.refresh(member)

        return member

    # ==========================================================
    # REFUSER UNE DEMANDE
    # ADMINISTRATION
    # ==========================================================

    def reject_request(
        self,
        request_id: uuid.UUID,
    ) -> MembershipRequest:

        request = self.db.get(
            MembershipRequest,
            request_id,
        )

        if request is None:
            raise ValueError(
                "Demande introuvable."
            )

        # ------------------------------------------------------
        # Vérifier si l'utilisateur est déjà membre
        # ------------------------------------------------------

        existing_member = self.db.scalar(
            select(Member).where(
                Member.user_id == request.user_id
            )
        )

        if existing_member is not None:
            raise ValueError(
                "Cet utilisateur est deja membre."
            )

        # ------------------------------------------------------
        # Une demande déjà rejetée reste rejetée
        # ------------------------------------------------------

        if request.status == "REJECTED":
            return request

        # ------------------------------------------------------
        # Une demande déjà approuvée ne peut pas être rejetée
        # ------------------------------------------------------

        if request.status == "APPROVED":
            raise ValueError(
                "Cette demande a deja ete approuvee."
            )

        # ------------------------------------------------------
        # Rejeter la demande
        # ------------------------------------------------------

        request.status = "REJECTED"

        # ------------------------------------------------------
        # Si le paiement avait été marqué payé, on le remet
        # en statut rejeté afin de garder une situation cohérente.
        # ------------------------------------------------------

        if request.payment_status == "PAID":
            request.payment_status = "REJECTED"

        self.db.commit()

        self.db.refresh(request)

        return request

    # ==========================================================
    # GENERER UN NUMERO DE MEMBRE UNIQUE
    # ==========================================================

    def generate_member_number(
        self,
    ) -> str:

        while True:

            number = (
                "MNPC-"
                + uuid.uuid4().hex[:8].upper()
            )

            existing_member = self.db.scalar(
                select(Member).where(
                    Member.member_number == number
                )
            )

            if existing_member is None:
                return number