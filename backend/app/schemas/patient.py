from datetime import date

from pydantic import BaseModel


# --------------------------------------------------
# CREATE PATIENT PROFILE
# --------------------------------------------------

class PatientCreate(BaseModel):
    date_of_birth: date | None = None
    gender: str | None = None
    address: str | None = None


# --------------------------------------------------
# PATIENT RESPONSE
# --------------------------------------------------

class PatientResponse(BaseModel):
    id: int
    user_id: int
    date_of_birth: date | None
    gender: str | None
    address: str | None

    class Config:
        from_attributes = True