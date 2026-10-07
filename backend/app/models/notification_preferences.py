from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    text
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("patients.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    whatsapp_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE")
    )

    sms_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE")
    )

    email_enabled: Mapped[bool] = mapped_column(
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