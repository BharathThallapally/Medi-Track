from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.patient import Patient
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.prescription_medicine import PrescriptionMedicine
from app.models.pharmacy import Pharmacy

from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionResponse
)

from app.schemas.prescription_medicine import (
    PrescriptionMedicineCreate,
    PrescriptionMedicineResponse
)


router = APIRouter(
    prefix="/prescriptions",
    tags=["Prescriptions"]
)


# ============================================================
# CREATE PRESCRIPTION
# ============================================================

@router.post(
    "",
    response_model=PrescriptionResponse
)
def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Only pharmacy users can create prescriptions
    # --------------------------------------------------------

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can create prescriptions"
        )

    # --------------------------------------------------------
    # Find pharmacy belonging to logged-in user
    # --------------------------------------------------------

    pharmacy = (
        db.query(Pharmacy)
        .filter(Pharmacy.user_id == current_user.id)
        .first()
    )

    if not pharmacy:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy profile not found"
        )

    # --------------------------------------------------------
    # Check patient
    # --------------------------------------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == prescription_data.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # --------------------------------------------------------
    # Create prescription
    # --------------------------------------------------------

    new_prescription = Prescription(
        patient_id=prescription_data.patient_id,
        doctor_id=prescription_data.doctor_id,
        pharmacy_id=pharmacy.id,
        prescription_date=prescription_data.prescription_date,
        prescription_image=prescription_data.prescription_image,
        status="ACTIVE"
    )

    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)

    return new_prescription


# ============================================================
# GET ALL PRESCRIPTIONS
# ============================================================

@router.get(
    "",
    response_model=list[PrescriptionResponse]
)
def get_prescriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can view prescriptions"
        )

    pharmacy = (
        db.query(Pharmacy)
        .filter(Pharmacy.user_id == current_user.id)
        .first()
    )

    if not pharmacy:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy profile not found"
        )

    prescriptions = (
        db.query(Prescription)
        .filter(
            Prescription.pharmacy_id == pharmacy.id
        )
        .order_by(Prescription.id.desc())
        .all()
    )

    return prescriptions


# ============================================================
# GET SINGLE PRESCRIPTION
# ============================================================

@router.get(
    "/{prescription_id}",
    response_model=PrescriptionResponse
)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can view prescriptions"
        )

    pharmacy = (
        db.query(Pharmacy)
        .filter(
            Pharmacy.user_id == current_user.id
        )
        .first()
    )

    if not pharmacy:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy profile not found"
        )

    prescription = (
        db.query(Prescription)
        .filter(
            Prescription.id == prescription_id,
            Prescription.pharmacy_id == pharmacy.id
        )
        .first()
    )

    if not prescription:
        raise HTTPException(
            status_code=404,
            detail="Prescription not found"
        )

    return prescription


# ============================================================
# ADD MEDICINE TO PRESCRIPTION
# ============================================================

@router.post(
    "/{prescription_id}/medicines",
    response_model=PrescriptionMedicineResponse
)
def add_medicine_to_prescription(
    prescription_id: int,
    medicine_data: PrescriptionMedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can add medicines"
        )

    # --------------------------------------------------------
    # Find pharmacy
    # --------------------------------------------------------

    pharmacy = (
        db.query(Pharmacy)
        .filter(
            Pharmacy.user_id == current_user.id
        )
        .first()
    )

    if not pharmacy:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy profile not found"
        )

    # --------------------------------------------------------
    # Check prescription
    # --------------------------------------------------------

    prescription = (
        db.query(Prescription)
        .filter(
            Prescription.id == prescription_id,
            Prescription.pharmacy_id == pharmacy.id
        )
        .first()
    )

    if not prescription:
        raise HTTPException(
            status_code=404,
            detail="Prescription not found"
        )

    # --------------------------------------------------------
    # Check medicine
    # --------------------------------------------------------

    medicine = (
        db.query(Medicine)
        .filter(
            Medicine.id == medicine_data.medicine_id
        )
        .first()
    )

    if not medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    # --------------------------------------------------------
    # Create prescription medicine
    # --------------------------------------------------------

    prescription_medicine = PrescriptionMedicine(
        prescription_id=prescription_id,
        medicine_id=medicine_data.medicine_id,
        dosage=medicine_data.dosage,
        frequency=medicine_data.frequency,
        timing=medicine_data.timing,
        food_instruction=medicine_data.food_instruction,
        duration_days=medicine_data.duration_days,
        quantity=medicine_data.quantity
    )

    db.add(prescription_medicine)
    db.commit()
    db.refresh(prescription_medicine)

    return prescription_medicine


# ============================================================
# GET MEDICINES IN PRESCRIPTION
# ============================================================

@router.get(
    "/{prescription_id}/medicines",
    response_model=list[PrescriptionMedicineResponse]
)
def get_prescription_medicines(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can view prescription medicines"
        )

    pharmacy = (
        db.query(Pharmacy)
        .filter(
            Pharmacy.user_id == current_user.id
        )
        .first()
    )

    if not pharmacy:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy profile not found"
        )

    prescription = (
        db.query(Prescription)
        .filter(
            Prescription.id == prescription_id,
            Prescription.pharmacy_id == pharmacy.id
        )
        .first()
    )

    if not prescription:
        raise HTTPException(
            status_code=404,
            detail="Prescription not found"
        )

    medicines = (
        db.query(PrescriptionMedicine)
        .filter(
            PrescriptionMedicine.prescription_id == prescription_id
        )
        .all()
    )

    return medicines