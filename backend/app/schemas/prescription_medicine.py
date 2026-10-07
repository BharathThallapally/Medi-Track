from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PrescriptionMedicineCreate(BaseModel):
    medicine_id: int
    dosage: str
    frequency: str
    timing: Optional[str] = None
    food_instruction: Optional[str] = None
    duration_days: int = Field(gt=0)
    quantity: int = Field(gt=0)


class PrescriptionMedicineResponse(BaseModel):
    id: int
    prescription_id: int
    medicine_id: int
    dosage: str
    frequency: str
    timing: Optional[str] = None
    food_instruction: Optional[str] = None
    duration_days: int
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True