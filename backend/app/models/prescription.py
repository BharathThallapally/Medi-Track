from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    String,
    Date,
    DateTime,
    Text,
    ForeignKey,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "patients.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # Doctor integration will be added later.
    # For now, this is stored without a foreign-key dependency.
    doctor_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )

    pharmacy_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "pharmacies.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    prescription_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE")
    )

    prescription_image: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )