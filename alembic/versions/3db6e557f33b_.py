"""empty message

Revision ID: 3db6e557f33b
Revises:
Create Date: 2026-08-25 21:28:45.108236
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3db6e557f33b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Cette migration ne doit rien modifier.
    #
    # Elle sert uniquement de migration de base.
    pass


def downgrade() -> None:
    """Downgrade schema."""

    # Rien à annuler.
    pass