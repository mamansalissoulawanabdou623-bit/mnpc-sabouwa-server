import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


if TYPE_CHECKING:
    from app.models.member import Member
    from app.models.organization_unit import OrganizationUnit
    from app.models.user import User


class OrganizationResponsible(Base):

    __tablename__ = "organization_responsibles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "organization_units.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "members.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    appointed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    position: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="RESPONSABLE",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ACTIVE",
    )

    appointed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    organization_unit: Mapped["OrganizationUnit"] = relationship(
        "OrganizationUnit",
        back_populates="responsible",
    )

    member: Mapped["Member"] = relationship(
        "Member",
    )

    appointed_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[appointed_by],
    )
