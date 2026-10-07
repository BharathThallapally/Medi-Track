from datetime import date

from pydantic import BaseModel


class ExpiryResponse(BaseModel):
    medicine_id: int
    batch_id: int
    batch_number: str
    expiry_date: date
    days_remaining: int
    status: str


class ExpiryListResponse(BaseModel):
    medicine_id: int
    medicine_name: str
    batch_id: int
    batch_number: str
    expiry_date: date
    days_remaining: int
    status: str