from datetime import datetime

from pydantic import BaseModel


class ConsentCreate(BaseModel):
    consent_type: str
    status: str


class ConsentResponse(BaseModel):
    id: int
    patient_id: int
    consent_type: str
    status: str
    given_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True