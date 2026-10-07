from datetime import datetime

from pydantic import BaseModel


class PurchaseMedicineCreate(BaseModel):
    purchase_id: int
    medicine_id: int
    batch_id: int
    quantity: int
    unit_price: float = 0.0


class PurchaseMedicineResponse(BaseModel):
    id: int
    purchase_id: int
    medicine_id: int
    batch_id: int
    quantity: int
    unit_price: float
    created_at: datetime

    class Config:
        from_attributes = True