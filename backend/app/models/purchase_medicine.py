from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Numeric,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PurchaseMedicine(Base):
    __tablename__ = "purchase_medicines"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    purchase_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("purchases.id", ondelete="CASCADE"),
        nullable=False
    )

    medicine_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medicines.id", ondelete="RESTRICT"),
        nullable=False
    )

    batch_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medicine_batches.id", ondelete="RESTRICT"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default=text("0.00")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )