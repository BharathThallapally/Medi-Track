from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Consent(Base):
    __tablename__ = "consents"

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

    consent_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    given_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )