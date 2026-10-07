from pydantic import BaseModel


# --------------------------------------------------
# CREATE MEDICINE
# --------------------------------------------------

class MedicineCreate(BaseModel):
    medicine_name: str
    generic_name: str | None = None
    strength: str | None = None
    dosage_form: str | None = None
    manufacturer: str | None = None


# --------------------------------------------------
# UPDATE MEDICINE
# --------------------------------------------------

class MedicineUpdate(BaseModel):
    medicine_name: str
    generic_name: str | None = None
    strength: str | None = None
    dosage_form: str | None = None
    manufacturer: str | None = None
    is_active: bool = True


# --------------------------------------------------
# MEDICINE RESPONSE
# --------------------------------------------------

class MedicineResponse(BaseModel):
    id: int
    medicine_name: str
    generic_name: str | None
    strength: str | None
    dosage_form: str | None
    manufacturer: str | None
    is_active: bool

    class Config:
        from_attributes = True