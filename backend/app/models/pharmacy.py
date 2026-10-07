from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    pharmacy_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    license_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    pincode: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
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