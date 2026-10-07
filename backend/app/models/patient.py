from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Patient(Base):
    __tablename__ = "patients"

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

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        Text,
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