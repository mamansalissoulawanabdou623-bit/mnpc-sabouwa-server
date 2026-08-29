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


class Finance(Base):

    __tablename__ = "finances"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


    member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "members.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )


    transaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )


    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="VALIDATED",
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda:
            datetime.now(timezone.utc),
        nullable=False,
    )