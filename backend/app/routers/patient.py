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

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# CREATE PATIENT
@router.post("", response_model=PatientResponse)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can create patients"
        )

    # Find the user account to link to this patient
    patient_user = (
        db.query(User)
        .filter(User.id == patient_data.user_id)
        .first()
    )

    if not patient_user:
        raise HTTPException(
            status_code=404,
            detail="Patient user account not found"
        )

    if patient_user.role != "PATIENT":
        raise HTTPException(
            status_code=400,
            detail="The selected user is not a patient account"
        )

    existing_patient = (
        db.query(Patient)
        .filter(Patient.user_id == patient_user.id)
        .first()
    )

    if existing_patient:
        raise HTTPException(
            status_code=409,
            detail="A patient profile already exists for this user"
        )

    new_patient = Patient(
        user_id=patient_user.id,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        address=patient_data.address
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


# GET ALL PATIENTS
@router.get("", response_model=list[PatientResponse])
def get_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can view patients"
        )

    return (
        db.query(Patient)
        .order_by(Patient.id.desc())
        .all()
    )


# GET SINGLE PATIENT
@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can view patients"
        )

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