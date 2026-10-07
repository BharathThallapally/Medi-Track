from pydantic import BaseModel


# --------------------------------------------------
# CREATE PHARMACY
# --------------------------------------------------

class PharmacyCreate(BaseModel):
    pharmacy_name: str
    license_number: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None


# --------------------------------------------------
# PHARMACY RESPONSE
# --------------------------------------------------

class PharmacyResponse(BaseModel):
    id: int
    user_id: int
    pharmacy_name: str
    license_number: str
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None

    class Config:
        from_attributes = True