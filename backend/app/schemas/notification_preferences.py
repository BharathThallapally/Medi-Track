from pydantic import BaseModel


class NotificationPreferenceCreate(BaseModel):
    whatsapp_enabled: bool = False
    sms_enabled: bool = False
    email_enabled: bool = True


class NotificationPreferenceResponse(BaseModel):
    id: int
    patient_id: int
    whatsapp_enabled: bool
    sms_enabled: bool
    email_enabled: bool

    class Config:
        from_attributes = True