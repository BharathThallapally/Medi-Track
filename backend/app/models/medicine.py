from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    medicine_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    generic_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    strength: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    dosage_form: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    manufacturer: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE")
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