"""add membership payment and card fields

Revision ID: add_member_card_fields
Revises: 3db6e557f33b
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_member_card_fields"
down_revision: Union[str, Sequence[str], None] = "3db6e557f33b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute les informations de paiement et de carte à la demande d'adhésion."""

    # ---------------------------------------------------------
    # ANCIENS CHAMPS DE CARTE SUR MEMBERS
    # ---------------------------------------------------------
    # Ces champs existent actuellement dans la base, mais ils
    # ne doivent plus être utilisés.
    #
    # La carte sera désormais gérée depuis membership_requests.
    # ---------------------------------------------------------

    op.drop_constraint(
        "uq_members_card_number",
        "members",
        type_="unique",
    )

    op.drop_column(
        "members",
        "card_expires_at",
    )

    op.drop_column(
        "members",
        "card_issued_at",
    )

    op.drop_column(
        "members",
        "card_number",
    )

    # ---------------------------------------------------------
    # NOUVEAUX CHAMPS SUR MEMBERSHIP_REQUESTS
    # ---------------------------------------------------------

    op.add_column(
        "membership_requests",
        sa.Column(
            "address",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "card_fee",
            sa.Float(),
            nullable=False,
            server_default="2000",
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "payment_status",
            sa.String(length=30),
            nullable=False,
            server_default="PENDING",
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "receipt_reference",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "receipt_url",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "payment_verified_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "card_started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "card_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Les valeurs par défaut ne sont nécessaires que pour
    # l'ajout des colonnes existantes.
    op.alter_column(
        "membership_requests",
        "card_fee",
        server_default=None,
    )

    op.alter_column(
        "membership_requests",
        "payment_status",
        server_default=None,
    )


def downgrade() -> None:
    """Restaure l'ancien système de carte."""

    # Supprimer les nouveaux champs de membership_requests
    # uniquement s'ils existent.

    op.drop_column(
        "membership_requests",
        "card_expires_at",
    )

    op.drop_column(
        "membership_requests",
        "card_started_at",
    )

    op.drop_column(
        "membership_requests",
        "payment_verified_at",
    )

    op.drop_column(
        "membership_requests",
        "receipt_url",
    )

    op.drop_column(
        "membership_requests",
        "receipt_reference",
    )

    op.drop_column(
        "membership_requests",
        "payment_status",
    )

    op.drop_column(
        "membership_requests",
        "card_fee",
    )

    op.drop_column(
        "membership_requests",
        "address",
    )

    # Restaurer les anciens champs de carte sur members.

    op.add_column(
        "members",
        sa.Column(
            "card_number",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "members",
        sa.Column(
            "card_issued_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "members",
        sa.Column(
            "card_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_members_card_number",
        "members",
        ["card_number"],
    )