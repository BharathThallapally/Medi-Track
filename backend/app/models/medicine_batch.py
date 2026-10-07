from datetime import date, datetime

from sqlalchemy import BigInteger, String, Date, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MedicineBatch(Base):
    __tablename__ = "medicine_batches"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    medicine_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medicines.id", ondelete="CASCADE"),
        nullable=False
    )

    batch_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    manufacturing_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    expiry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
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