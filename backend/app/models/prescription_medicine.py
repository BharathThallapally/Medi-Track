from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PrescriptionMedicine(Base):
    __tablename__ = "prescription_medicines"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    prescription_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False
    )

    medicine_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medicines.id", ondelete="RESTRICT"),
        nullable=False
    )

    dosage: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    frequency: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    timing: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    food_instruction: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    duration_days: Mapped[int] = mapped_column(
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )