from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_id: Optional[int] = None
    prescription_date: Optional[date] = None
    prescription_image: Optional[str] = None


class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: Optional[int] = None
    pharmacy_id: int
    prescription_date: date
    prescription_image: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True