from datetime import date

from pydantic import BaseModel


class MedicineBatchCreate(BaseModel):
    medicine_id: int
    batch_number: str
    manufacturing_date: date | None = None
    expiry_date: date


class MedicineBatchUpdate(BaseModel):
    batch_number: str
    manufacturing_date: date | None = None
    expiry_date: date


class MedicineBatchResponse(BaseModel):
    id: int
    medicine_id: int
    batch_number: str
    manufacturing_date: date | None
    expiry_date: date

    class Config:
        from_attributes = True