import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MembershipRequest(Base):

    __tablename__ = "membership_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    organization_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization_units.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    # =========================
    # IDENTITE
    # =========================

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    birth_date: Mapped[datetime | None] = mapped_column(
        Date,
        nullable=True,
    )

    birth_place: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    nationality: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # =========================
    # LOCALISATION
    # =========================

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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

    village_quartier: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    # =========================
    # SITUATION
    # =========================

    profession: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    education_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    skills_experience: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    requested_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    motivation: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # =========================
    # PHOTO
    # =========================

    photo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # =========================
    # VALIDATION
    # =========================

    statutes_accepted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    declaration_accepted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # =========================
    # PAIEMENT
    # =========================

    card_fee: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=2000.0,
    )

    payment_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    receipt_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    receipt_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    payment_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================
    # CARTE
    # =========================

    card_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    card_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================
    # DATES
    # =========================

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