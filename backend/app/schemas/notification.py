from datetime import datetime

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    patient_id: int
    medicine_id: int | None = None
    batch_id: int | None = None
    notification_type: str
    channel: str
    scheduled_at: datetime


class NotificationResponse(BaseModel):
    id: int
    patient_id: int
    medicine_id: int | None
    batch_id: int | None
    notification_type: str
    channel: str
    scheduled_at: datetime
    sent_at: datetime | None
    status: str
    provider_reference: str | None
    created_at: datetime

    class Config:
        from_attributes = True