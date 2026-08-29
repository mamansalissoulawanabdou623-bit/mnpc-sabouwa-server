import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


if TYPE_CHECKING:
    from app.models.member import Member
    from app.models.organization_responsible import OrganizationResponsible


class OrganizationUnit(Base):

    __tablename__ = "organization_units"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "organization_units.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    unit_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    region: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    commune: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ACTIVE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    parent: Mapped["OrganizationUnit | None"] = relationship(
        "OrganizationUnit",
        remote_side="OrganizationUnit.id",
        back_populates="children",
    )

    children: Mapped[list["OrganizationUnit"]] = relationship(
        "OrganizationUnit",
        back_populates="parent",
    )

    members: Mapped[list["Member"]] = relationship(
        "Member",
        back_populates="organization_unit",
    )

    responsible: Mapped["OrganizationResponsible | None"] = relationship(
        "OrganizationResponsible",
        back_populates="organization_unit",
        uselist=False,
    )
