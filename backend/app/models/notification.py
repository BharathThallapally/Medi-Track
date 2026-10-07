from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False
    )

    medicine_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("medicines.id", ondelete="SET NULL"),
        nullable=True
    )

    batch_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("medicine_batches.id", ondelete="SET NULL"),
        nullable=True
    )

    notification_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'PENDING'")
    )

    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )