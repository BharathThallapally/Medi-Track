from datetime import date

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    user_id: int = Field(gt=0)
    date_of_birth: date | None = None
    gender: str | None = None
    address: str | None = None


class PatientResponse(BaseModel):
    id: int
    user_id: int
    date_of_birth: date | None = None
    gender: str | None = None
    address: str | None = None

    class Config:
        from_attributes = True