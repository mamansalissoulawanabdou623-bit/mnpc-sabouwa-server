import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class NationalStatistic(Base):

    __tablename__ = "national_statistics"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


    statistic_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


    year: Mapped[int] = mapped_column(
        Integer,
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


    total_members: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    total_men: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    total_women: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    total_youth: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )