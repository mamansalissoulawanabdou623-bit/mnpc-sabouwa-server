"""complete membership request fields

Revision ID: 83b51e251c5d
Revises: f8078c1b3d9a
Create Date: 2026-09-02 10:24:41.877428

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "83b51e251c5d"
down_revision: Union[str, Sequence[str], None] = "f8078c1b3d9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "membership_requests",
        sa.Column(
            "gender",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "birth_date",
            sa.Date(),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "birth_place",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "nationality",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "region",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "department",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "commune",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "village_quartier",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "profession",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "education_level",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "skills_experience",
            sa.String(length=1000),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "requested_status",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "motivation",
            sa.String(length=1000),
            nullable=True,
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "photo_url",
            sa.String(length=500),
            nullable=True,
        ),
    )

    # Ces deux colonnes sont obligatoires.
    # Les anciennes demandes recevront automatiquement FALSE.
    op.add_column(
        "membership_requests",
        sa.Column(
            "statutes_accepted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "membership_requests",
        sa.Column(
            "declaration_accepted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "membership_requests",
        "declaration_accepted",
    )

    op.drop_column(
        "membership_requests",
        "statutes_accepted",
    )

    op.drop_column(
        "membership_requests",
        "photo_url",
    )

    op.drop_column(
        "membership_requests",
        "motivation",
    )

    op.drop_column(
        "membership_requests",
        "requested_status",
    )

    op.drop_column(
        "membership_requests",
        "skills_experience",
    )

    op.drop_column(
        "membership_requests",
        "education_level",
    )

    op.drop_column(
        "membership_requests",
        "profession",
    )

    op.drop_column(
        "membership_requests",
        "village_quartier",
    )

    op.drop_column(
        "membership_requests",
        "commune",
    )

    op.drop_column(
        "membership_requests",
        "department",
    )

    op.drop_column(
        "membership_requests",
        "region",
    )

    op.drop_column(
        "membership_requests",
        "nationality",
    )

    op.drop_column(
        "membership_requests",
        "birth_place",
    )

    op.drop_column(
        "membership_requests",
        "birth_date",
    )

    op.drop_column(
        "membership_requests",
        "gender",
    )