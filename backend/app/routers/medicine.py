from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db

from app.models.user import User
from app.models.medicine import Medicine

from app.schemas.medicine import (
    MedicineCreate,
    MedicineUpdate,
    MedicineResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/medicines",
    tags=["Medicine"]
)


# ============================================================
# ROLE CHECK
# ============================================================

def check_pharmacy_role(current_user: User):
    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can manage medicines"
        )


# ============================================================
# CREATE MEDICINE
# ============================================================

@router.post(
    "",
    response_model=MedicineResponse
)
def create_medicine(
    medicine_data: MedicineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    medicine = Medicine(
        medicine_name=medicine_data.medicine_name,
        generic_name=medicine_data.generic_name,
        strength=medicine_data.strength,
        dosage_form=medicine_data.dosage_form,
        manufacturer=medicine_data.manufacturer
    )

    db.add(medicine)
    db.commit()
    db.refresh(medicine)

    return medicine


# ============================================================
# GET ALL ACTIVE MEDICINES
# ============================================================

@router.get(
    "",
    response_model=list[MedicineResponse]
)
def get_medicines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    medicines = (
        db.query(Medicine)
        .filter(Medicine.is_active == True)
        .order_by(Medicine.id)
        .all()
    )

    return medicines


# ============================================================
# GET MEDICINE BY ID
# ============================================================

@router.get(
    "/{medicine_id}",
    response_model=MedicineResponse
)
def get_medicine(
    medicine_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    medicine = (
        db.query(Medicine)
        .filter(
            Medicine.id == medicine_id,
            Medicine.is_active == True
        )
        .first()
    )

    if not medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    return medicine


# ============================================================
# UPDATE MEDICINE
# ============================================================

@router.put(
    "/{medicine_id}",
    response_model=MedicineResponse
)
def update_medicine(
    medicine_id: int,
    medicine_data: MedicineUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    medicine = (
        db.query(Medicine)
        .filter(
            Medicine.id == medicine_id,
            Medicine.is_active == True
        )
        .first()
    )

    if not medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    medicine.medicine_name = medicine_data.medicine_name
    medicine.generic_name = medicine_data.generic_name
    medicine.strength = medicine_data.strength
    medicine.dosage_form = medicine_data.dosage_form
    medicine.manufacturer = medicine_data.manufacturer

    if medicine_data.is_active is not None:
        medicine.is_active = medicine_data.is_active

    db.commit()
    db.refresh(medicine)

    return medicine


# ============================================================
# DELETE / DEACTIVATE MEDICINE
# ============================================================

@router.delete(
    "/{medicine_id}"
)
def delete_medicine(
    medicine_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    medicine = (
        db.query(Medicine)
        .filter(
            Medicine.id == medicine_id,
            Medicine.is_active == True
        )
        .first()
    )

    if not medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    # Soft delete
    medicine.is_active = False

    db.commit()

    return {
        "message": "Medicine deleted successfully",
        "medicine_id": medicine.id
    }