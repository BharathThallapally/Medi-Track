from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ============================================================
# CREATE PURCHASE
# ============================================================

class PurchaseCreate(BaseModel):
    patient_id: int

    # Prescription is optional
    prescription_id: Optional[int] = None

    total_amount: float

    # ========================================================
    # PATIENT CONTACT DETAILS
    # ========================================================

    # Pharmacy can enter/update the patient's email
    email: Optional[EmailStr] = None

    # Patient's mobile number.
    # This number can be used for WhatsApp and/or SMS.
    phone: Optional[str] = None

    # ========================================================
    # NOTIFICATION CHANNELS
    # ========================================================

    # Pharmacy decides which channels should be used
    email_enabled: bool = False
    whatsapp_enabled: bool = False
    sms_enabled: bool = False


# ============================================================
# PURCHASE RESPONSE
# ============================================================

class PurchaseResponse(BaseModel):
    id: int
    patient_id: int
    pharmacy_id: int
    prescription_id: Optional[int] = None
    total_amount: float
    created_at: datetime

    class Config:
        from_attributes = True