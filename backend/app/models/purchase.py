from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Purchase(Base):
    __tablename__ = "purchases"

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

    pharmacy_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("pharmacies.id", ondelete="CASCADE"),
        nullable=False
    )

    prescription_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("prescriptions.id", ondelete="SET NULL"),
        nullable=True
    )

    purchase_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default=text("0.00")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # -----------------------------------------------------
    # Digital medicine sheet delivery tracking
    # -----------------------------------------------------

    medicine_sheet_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )