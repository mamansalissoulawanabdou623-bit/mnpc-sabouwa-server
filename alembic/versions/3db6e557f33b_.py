"""Fix organization units indexes and foreign key.

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

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = inspector.get_table_names()

    # ============================================================
    # ORGANIZATION_UNITS
    # ============================================================

    if "organization_units" in tables:

        indexes = {
            index["name"]
            for index in inspector.get_indexes("organization_units")
        }

        # Supprimer l'index seulement s'il existe
        parent_index = op.f("ix_organization_units_parent_id")

        if parent_index in indexes:
            op.drop_index(
                parent_index,
                table_name="organization_units",
            )

        # Supprimer l'index seulement s'il existe
        unit_type_index = op.f("ix_organization_units_unit_type")

        if unit_type_index in indexes:
            op.drop_index(
                unit_type_index,
                table_name="organization_units",
            )

        # ========================================================
        # FOREIGN KEY parent_id
        # ========================================================

        foreign_keys = inspector.get_foreign_keys(
            "organization_units"
        )

        old_fk_name = op.f(
            "organization_units_parent_id_fkey"
        )

        old_fk_exists = any(
            fk.get("name") == old_fk_name
            for fk in foreign_keys
        )

        if old_fk_exists:
            op.drop_constraint(
                old_fk_name,
                "organization_units",
                type_="foreignkey",
            )

        # Vérifier à nouveau les clés étrangères
        inspector = sa.inspect(bind)

        foreign_keys_after = inspector.get_foreign_keys(
            "organization_units"
        )

        parent_fk_exists = any(
            fk.get("constrained_columns") == ["parent_id"]
            and fk.get("referred_table") == "organization_units"
            and fk.get("referred_columns") == ["id"]
            for fk in foreign_keys_after
        )

        # Créer la nouvelle relation uniquement si elle n'existe pas
        if not parent_fk_exists:
            op.create_foreign_key(
                "fk_organization_units_parent_id",
                "organization_units",
                "organization_units",
                ["parent_id"],
                ["id"],
                ondelete="RESTRICT",
            )

    # ============================================================
    # USERS
    # ============================================================

    if "users" in tables:

        user_indexes = {
            index["name"]
            for index in inspector.get_indexes("users")
        }

        member_index = op.f("ix_users_member_id")

        # Supprimer l'index seulement s'il existe
        if member_index in user_indexes:
            op.drop_index(
                member_index,
                table_name="users",
            )


def downgrade() -> None:
    """Downgrade schema."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = inspector.get_table_names()

    # ============================================================
    # USERS
    # ============================================================

    if "users" in tables:

        user_indexes = {
            index["name"]
            for index in inspector.get_indexes("users")
        }

        member_index = op.f("ix_users_member_id")

        if member_index not in user_indexes:
            op.create_index(
                member_index,
                "users",
                ["member_id"],
                unique=False,
            )

    # ============================================================
    # ORGANIZATION_UNITS
    # ============================================================

    if "organization_units" in tables:

        foreign_keys = inspector.get_foreign_keys(
            "organization_units"
        )

        fk_name = "fk_organization_units_parent_id"

        fk_exists = any(
            fk.get("name") == fk_name
            for fk in foreign_keys
        )

        if fk_exists:
            op.drop_constraint(
                fk_name,
                "organization_units",
                type_="foreignkey",
            )

        inspector = sa.inspect(bind)

        foreign_keys = inspector.get_foreign_keys(
            "organization_units"
        )

        old_fk_name = op.f(
            "organization_units_parent_id_fkey"
        )

        old_fk_exists = any(
            fk.get("name") == old_fk_name
            for fk in foreign_keys
        )

        if not old_fk_exists:
            op.create_foreign_key(
                old_fk_name,
                "organization_units",
                "organization_units",
                ["parent_id"],
                ["id"],
                ondelete="SET NULL",
            )

        # Recréer l'index parent_id s'il n'existe pas
        inspector = sa.inspect(bind)

        indexes = {
            index["name"]
            for index in inspector.get_indexes(
                "organization_units"
            )
        }

        parent_index = op.f(
            "ix_organization_units_parent_id"
        )

        if parent_index not in indexes:
            op.create_index(
                parent_index,
                "organization_units",
                ["parent_id"],
                unique=False,
            )

        # Recréer l'index unit_type s'il n'existe pas
        inspector = sa.inspect(bind)

        indexes = {
            index["name"]
            for index in inspector.get_indexes(
                "organization_units"
            )
        }

        unit_type_index = op.f(
            "ix_organization_units_unit_type"
        )

        if unit_type_index not in indexes:
            op.create_index(
                unit_type_index,
                "organization_units",
                ["unit_type"],
                unique=False,
            )
