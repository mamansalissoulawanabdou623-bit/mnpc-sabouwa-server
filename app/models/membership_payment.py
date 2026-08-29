import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MembershipPayment(Base):

    __tablename__ = "membership_payments"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "members.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=2000.0,
    )


    payment_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


    transaction_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


    receipt_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )


    payment_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )


    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )