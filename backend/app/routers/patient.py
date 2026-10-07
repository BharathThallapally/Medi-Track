from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.patient import Patient

from app.schemas.patient import (
    PatientCreate,
    PatientResponse
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# ============================================================
# CREATE PATIENT
# ============================================================

@router.post(
    "",
    response_model=PatientResponse
)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Only pharmacy users can create patients
    # --------------------------------------------------------

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can create patients"
        )

    # --------------------------------------------------------
    # Create patient
    # --------------------------------------------------------

    new_patient = Patient(
        user_id=patient_data.user_id
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


# ============================================================
# GET ALL PATIENTS
# ============================================================

@router.get(
    "",
    response_model=list[PatientResponse]
)
def get_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Only pharmacy users can view patients
    # --------------------------------------------------------

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can view patients"
        )

    # --------------------------------------------------------
    # Get all patients
    # --------------------------------------------------------

    patients = (
        db.query(Patient)
        .order_by(Patient.id.desc())
        .all()
    )

    return patients


# ============================================================
# GET SINGLE PATIENT
# ============================================================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Only pharmacy users can view patients
    # --------------------------------------------------------

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can view patients"
        )

    # --------------------------------------------------------
    # Find patient
    # --------------------------------------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient